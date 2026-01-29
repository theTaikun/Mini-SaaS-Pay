from flask import Blueprint, jsonify, request, session
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert

from definitions import SessionLocal
from models import User

user_bp = Blueprint('user_bp', __name__)

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
            .on_conflict_do_nothing(
                index_elements=["email"],
            )
            .returning(User.id)
        )
        response = conn.execute(stmt).mappings().one()
        conn.commit()
        conn.close()
    session["id"] = response.id
    return dict(response), 201
