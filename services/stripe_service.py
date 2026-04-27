import os
from flask import g
from sqlalchemy import select, update
import stripe

from definitions import get_db, PUBLIC_URL, STRIPE_EVENT_TYPES, DEFAULT_PRICE_ID
from models import User
from services.user_service import complete_onboarding

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY


def syncStripeDataToKV(customerId: str):
    subscriptions = stripe.Subscription.list(
            customer=customerId,
            limit=1,
            status="all",
            expand=["data.default_payment_method"]
    )
    if len(subscriptions.data) == 0:
        subData = {"status": None}

    else:
        # Number of subscriptions per user should have already been limitted to one
        subscription = subscriptions.data[0]
        subscription_item = subscription["items"]["data"][0]

        subData = {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "price_id": subscription_item.price.id,
            "current_period_start": subscription_item.current_period_start,
            "current_period_end": subscription_item.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            # "payment_method": {}, # recommended by t3dotgg, but not needed
            "product_id": subscription_item.plan.product,
            }

    return subData


def create_stripe_customer(user_email):
    new_customer = stripe.Customer.create(
        email=user_email
        # TODO: add metadata for stripe side where app_user_id=User.id
    )

    stmt = (
        update(User)
        .where(User.email == user_email)
        .values(customer_id = new_customer.id)
        )
    with get_db() as conn:
        conn.execute(stmt)
        conn.commit()

    return new_customer


def create_stripe_checkout(customer, price_id=DEFAULT_PRICE_ID):
    stripe_session = stripe.checkout.Session.create(
        customer=customer.id,
        payment_method_types=["card"],
        payment_method_collection="if_required",
        mode="subscription",
        line_items=[{
            "price": price_id,
            "quantity": 1,
            }],
        success_url=f"{ PUBLIC_URL }/success/",
        cancel_url=f"{ PUBLIC_URL }/cancel/",
        )
    return stripe_session


def create_new_stripe_checkout(user_email, price_id):
    new_customer = create_stripe_customer(user_email)
    stripe_session = create_stripe_checkout(new_customer, price_id)
    return stripe_session


def create_stripe_customer_session(customer_id):
    customer_session = stripe.v1.customer_sessions.create({
        "customer": customer_id,
        "components": {"pricing_table": {"enabled": True}},
        })
    return customer_session.client_secret


def get_user_by_stripe_id(stripe_id):
    stmt = (
        select(User)
        .where(User.customer_id == stripe_id)
        )
    with get_db() as conn:
        user = conn.execute(stmt)
    return user


def stripe_successful_payment(app_user_id):
        with get_db() as conn:
            stmt = select(User.customer_id).where(User.id==app_user_id)
            customer_id = conn.execute(stmt).scalar_one()
            subData = syncStripeDataToKV(customer_id)
            stmt = (
                update(User)
                .where(User.id==app_user_id)
                .values(**subData)
            )
            conn.execute(stmt)
            conn.commit()
        complete_onboarding(app_user_id)
        subData.update({
            "onboarding_completed": True, # reimplemented since other function requires users.id
            "customer_id": customer_id
            })
        return subData


def stripe_webhook_handler(request):
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET") # Get from Stripe webhook setup

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        raise Exception("Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise Exception("Invalid signature")

    if event["type"] in STRIPE_EVENT_TYPES:
        stripe_session = event["data"]["object"]
        customer = stripe_session["customer"]
        print("Webhook initiated for ", customer)
        subData = syncStripeDataToKV(customer)
        subData["onboarding_completed"] = True # reimplemented since other function requires users.id
        stmt = (
            update(User)
            .where(User.customer_id==customer)
            .values(**subData)
        )
        # TODO: handle user not found
        # This error occurs if using stripe CLI trigger,
        #   as it creates a random user, who is not already in app db
        with get_db() as conn:
            conn.execute(stmt)
            conn.commit()

        return { "customer_id": customer, **subData}
