from flask import Blueprint, jsonify, request, render_template_string, session
import os
from sqlalchemy import select, update
import stripe

from definitions import SessionLocal, STRIPE_EVENT_TYPES
from models import User
from utils import syncStripeDataToKV

stripe_bp = Blueprint('stripe', __name__)

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY


@stripe_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        data = request.json
        new_customer = stripe.Customer.create(
            email=data["userEmail"]
        )

        stmt = (
            update(User)
            .where(User.id==session["id"])
            .values(customer_id=new_customer.id)
            )
        with SessionLocal() as conn:
            conn.execute(stmt)
            conn.commit()
            conn.close()

        stripe_session = stripe.checkout.Session.create(
            customer=new_customer.id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{
                "price": data["price_id"],  # Price ID from Stripe
                "quantity": 1,
                }],
            success_url="http://localhost:5000/success/",
            cancel_url="http://localhost:5000/cancel/",
            )
        return jsonify({"id": stripe_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 400

@stripe_bp.route("/success/", methods=["GET"])
def successful_checkout():
    # Rather than using the session_id stripe sends,
    # pull info using stored customer_id
    if "id" in session:
        with SessionLocal() as conn:
            stmt = select(User.customer_id).where(User.id==session["id"])
            response = conn.execute(stmt).scalar_one()
            subData = syncStripeDataToKV(response)
            stmt = (
                update(User)
                .where(User.id==session["id"])
                .values(**subData)
            )
            with SessionLocal() as conn:
                conn.execute(stmt)
                conn.commit()
        session.update(subData)
        return render_template_string(f'Success! Syncing your data, user #{session["id"]}')
    else:
        return render_template_string('Please login first <a href="/">Login</a>')

@stripe_bp.route("/cancel/", methods=["GET"])
def cancel_checkout():
    return render_template_string("Oh... Ok Then... :(")

@stripe_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET") # Get from Stripe webhook setup

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] in STRIPE_EVENT_TYPES:
        stripe_session = event["data"]["object"]
        customer = stripe_session["customer"]
        print("Webhook initiated for ", customer)
        subData = syncStripeDataToKV(customer)
        stmt = (
            update(User)
            .where(User.customer_id==customer)
            .values(**subData)
        )
        # TODO: handle user not found
        # This error occurs if using stripe CLI trigger,
        #   as it creates a random user, who is not already in app db
        with SessionLocal() as conn:
            conn.execute(stmt)
            conn.commit()

        session.update(subData)


    return "Success", 200

