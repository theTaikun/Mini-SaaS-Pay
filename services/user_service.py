from flask import g
from sqlalchemy import select, update
from sqlalchemy.dialects.sqlite import insert

from definitions import get_db
from models import User


def create_user(username, password):
    user = User(
        email=username,
        password=password,
        )
    with get_db() as conn:
        conn.add(user)
        id = user.id
        conn.commit() # this line will raise exception if unique constraint fail

    return id

def login_user(username, password):
    stmt = (
        select(User)
        .where(User.email==username, User.password==password)
    )
    with get_db() as conn:
        response = conn.execute(stmt)
        result= response.scalar_one_or_none()
        conn.close()
    if result:
        res_dict = result.__dict__
        del res_dict["password"]
        del res_dict["_sa_instance_state"]
        return res_dict
    else:
        return None

def complete_onboarding(app_user_id):
    stmt = (
        update(User)
        .where(User.id==app_user_id)
        .values(onboarding_completed = True)
        )
    with get_db() as conn:
        conn.execute(stmt)
        conn.commit()
        conn.close()
