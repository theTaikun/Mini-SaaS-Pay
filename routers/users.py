from flask import Blueprint, jsonify, redirect, request, session, url_for

from services.user_service import complete_onboarding, create_user, login_user

user_bp = Blueprint('user_bp', __name__)


@user_bp.route("/user", methods=["PATCH"])
def update_user_endpoint():
    data = request.json
    if data["onboarded"]:
        complete_onboarding(session["id"])
        session["onboarding_completed"] = True
    return "Success", 200


@user_bp.route("/user", methods=["POST"])
def new_user_endpoint():
    data = request.json
    try:
        response = create_user(username=data["email"], password=data["password"])
        return dict(response), 201
    except:
        return jsonify(error="user already exists"), 409


@user_bp.route("/login/", methods=["POST"])
def login_endpoint():
    data = request.json
    res_dict = login_user(username=data["username"], password=data["password"])
    if res_dict:
        session.update(res_dict)
        return jsonify({"status":"Success"}), 200
    else:
        return jsonify({"status":"Invalid Login"}), 401


@user_bp.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for('home'))


