from sqlalchemy import select, update

from definitions import get_db, PROD_MAP
from models import User


def create_user(username, password):
    user = User(
        email=username,
        password=password,
        )
    with get_db() as conn:
        conn.add(user)
        user_id = user.id # must capture because 'user' disappears after commit
        conn.commit() # this line will raise exception if unique constraint fail

    return user_id


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


def is_enable_premium_feature(app_user_id):
    stmt = select(User.product_id).where(User.id==app_user_id)
    with get_db() as conn:
        product_id = conn.execute(stmt).scalar_one()

    return "PREMIUM_FEATURE" in PROD_MAP[product_id]["features"]


def is_enable_ultimate_feature(app_user_id):
    stmt = select(User.product_id).where(User.id==app_user_id)
    with get_db() as conn:
        product_id = conn.execute(stmt).scalar_one()

    return "ULTIMATE_FEATURE" in PROD_MAP[product_id]["features"]
