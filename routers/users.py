from flask import Blueprint, jsonify, redirect, request, session, url_for
from sqlalchemy import select, update
from sqlalchemy.dialects.sqlite import insert

from definitions import SessionLocal
from models import User

user_bp = Blueprint('user_bp', __name__)


def complete_onboarding():
    stmt = (
        update(User)
        .where(User.id==session["id"])
        .values(onboarding_completed = True)
        )
    with SessionLocal() as conn:
        conn.execute(stmt)
        conn.commit()
        conn.close()
    session["onboarding_completed"] = True


@user_bp.route("/user", methods=["PATCH"])
def update_user():
    data = request.json
    if data["onboarded"]:
        complete_onboarding()
    return "Success", 200


@user_bp.route("/user", methods=["POST"])
def add_user():
    with SessionLocal() as conn:
        data = request.json
        stmt = (
            select(User).where(User.email==data["email"])
            )
        response = conn.execute(stmt).one_or_none()
        if response:
            return jsonify(error="user already exists"), 409

        stmt = (
            insert(User)
            .values(
                {
                    "email": data["email"],
                    "password": data["password"],
                }
            )
            .on_conflict_do_nothing( # TODO: handle conflict? shouldn't happen
                index_elements=["email"],
            )
            .returning(User.id)
        )
        response = conn.execute(stmt).mappings().one()
        conn.commit()
        conn.close()
    return dict(response), 201


@user_bp.route("/login/", methods=["POST"])
def login_submitted():
    data = request.json
    stmt = (
        select(User)
        .where(User.email==data["username"], User.password==data["password"])
    )
    with SessionLocal() as conn:
        response = conn.execute(stmt)
        result= response.scalar_one_or_none()
        conn.close()
    if result:
        res_dict = result.__dict__
        del res_dict["password"]
        del res_dict["_sa_instance_state"]
        session.update(res_dict)
        return jsonify({"status":"Success"}), 200
    else:
        return jsonify({"status":"Invalid Login"}), 401


@user_bp.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for('home'))


