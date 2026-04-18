from flask import Blueprint, jsonify, request, render_template_string, session

from services.stripe_service import create_stripe_customer, create_stripe_checkout, create_new_stripe_checkout, get_user_by_id, stripe_successful_payment, stripe_webhook_handler

stripe_bp = Blueprint('stripe', __name__)


@stripe_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    try:
        stripe_session = create_new_stripe_checkout(user_email=data["userEmail"], price_id = data["price_id"])
        return jsonify({"id": stripe_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 400

@stripe_bp.route("/success/", methods=["GET"])
def successful_checkout_endpoint():
    # Rather than using the session_id stripe sends,
    # pull info using stored customer_id
    if "id" in session:
        subData_onboarding_cust_id = stripe_successful_payment(app_user_id = session["id"])
        session.update(subData_onboarding_cust_id)
        return render_template_string(f'Success! Syncing your data, user #{session["id"]} <a href="/">Login</a>')
    else:
        return render_template_string('Please login first <a href="/">Login</a>')

@stripe_bp.route("/cancel/", methods=["GET"])
def cancel_checkout():
    return render_template_string("Oh... Ok Then... :(")

@stripe_bp.route("/webhook", methods=["POST"])
def webhook_endpoint():
    try:
        subData = stripe_webhook_handler(request)
        session.update(subData)
    except Exception as e:
        return str(e), 400 # TODO: don't expose internal errors, predefine string
    return "Success", 200

