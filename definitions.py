import os
from dotenv import load_dotenv
from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

"""
only needed because published to open source
avoids disclosing stripe ids,
    which, while not secret,
    may not want to be published
in pivate repo, better to just skip prod_price_ids,
    and just hardcode into PROD_MAP
"""
from prod_price_ids import (
    FREE_PROD_ID,
    PRO_PROD_ID,
    ELITE_PROD_ID,

    FREE_MONTHLY_PRICE_ID,
    FREE_YEARLY_PRICE_ID,
    PRO_MONTHLY_PRICE_ID,
    PRO_YEARLY_PRICE_ID,
    ELITE_MONTHLY_PRICE_ID,
    ELITE_YEARLY_PRICE_ID,
)

USE_STRIPE_PRICING_TABLE = True

load_dotenv()

DB_URI = os.getenv("DB_URI")
PUBLIC_URL = os.getenv("PUBLIC_URL")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_PRICING_TABLE_ID = os.getenv("STRIPE_PRICING_TABLE_ID")


def init_engine(database_url):
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False}
        )

def init_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    if "db" not in g:
        session_factory = current_app.session_factory
        g.db = session_factory()
    return g.db

def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        if exception:
            db.rollback()
        else:
            db.commit()
        db.close()


PROD_MAP = {
    FREE_PROD_ID: {
        "name": "free",
        "features": [],
        "price_ids": {
            "monthly": FREE_MONTHLY_PRICE_ID,
            "yearly": FREE_YEARLY_PRICE_ID,
            },
        },
    PRO_PROD_ID: {
        "name": "pro",
        "features": [
            "PREMIUM_FEATURE",
            ],
        "price_ids": {
            "monthly": PRO_MONTHLY_PRICE_ID,
            "yearly": PRO_YEARLY_PRICE_ID,
            },
        },
    ELITE_PROD_ID: {
        "name": "elite",
        "features": [
            "PREMIUM_FEATURE",
            "ULTIMATE_FEATURE",
            ],
        "price_ids": {
            "monthly": ELITE_MONTHLY_PRICE_ID,
            "yearly": ELITE_YEARLY_PRICE_ID,
            },
        },
    }

DEFAULT_PRICE_ID = [ PROD_MAP[x]["price_ids"]["monthly"] for x in PROD_MAP if  PROD_MAP[x]["name"] == "free"][0]

# These should be configured in Stripe itself as well
# Otherwise listen to all messages and filter them here,
# but then there will be a ton of traffic to the webhook endpoint
STRIPE_EVENT_TYPES = [
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "customer.subscription.paused",
    "customer.subscription.resumed",
    "customer.subscription.pending_update_applied",
    "customer.subscription.pending_update_expired",
    "customer.subscription.trial_will_end",
    "invoice.paid",
    "invoice.payment_failed",
    "invoice.payment_action_required",
    "invoice.upcoming",
    "invoice.marked_uncollectible",
    "invoice.payment_succeeded",
    "payment_intent.succeeded",
    "payment_intent.payment_failed",
    "payment_intent.canceled",
    ]
