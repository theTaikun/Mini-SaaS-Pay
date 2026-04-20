import os
from dotenv import load_dotenv
from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_URI = os.getenv("DB_URI")
PUBLIC_URL = os.getenv("PUBLIC_URL")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_RECURRING_PRICE_ID = os.getenv("STRIPE_RECURRING_PRICE_ID")

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
