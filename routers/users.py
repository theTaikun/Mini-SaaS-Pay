from flask import Blueprint, jsonify, redirect, request, session, url_for
from sqlalchemy.exc import IntegrityError

from services.user_service import complete_onboarding, create_user, login_user
from services.stripe_service import create_stripe_customer

user_bp = Blueprint('user_bp', __name__)


@user_bp.route("/user", methods=["PATCH"])
def update_user_endpoint():
    data = request.json
    if data["onboarded"]:
        complete_onboarding(session["id"])
        session["onboarding_completed"] = True
    return "Success", 200


# TODO: Create stripe customer first? so single User creation and no update?
@user_bp.route("/user", methods=["POST"])
def new_user_endpoint():
    data = request.json
    try:
        app_user_id = create_user(username=data["email"], password=data["password"])
    except IntegrityError:
        return jsonify(error="user already exists"), 409

    # TODO: Pass app_user_id rather than email?
    create_stripe_customer(data["email"])

    return { "id": app_user_id }, 201

@user_bp.route("/login/", methods=["POST"])
def login_endpoint():
    data = request.json
    res_dict = login_user(username=data["username"], password=data["password"])
    if res_dict:
        session.update(res_dict)
        return jsonify({"status":"Success"}), 200
    return jsonify({"status":"Invalid Login"}), 401


@user_bp.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for('home'))
