from flask import Blueprint, jsonify, request
import os
import stripe

stripe_bp = Blueprint('stripe', __name__)

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY


@stripe_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        data = request.json
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{
                "price": data["price_id"],  # Price ID from Stripe
                "quantity": 1,
                }],
            success_url="http://localhost:5000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:5000/cancel",
            )
        return jsonify({"id": session.id})
    except Exception as e:
        return jsonify(error=str(e)), 400



@stripe_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = "whsec_..."  # Get from Stripe webhook setup

    try:
        event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
                )
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
    # Here, activate the user account / grant access
        print("Payment succeeded for", session["customer_email"])

    return "", 200

