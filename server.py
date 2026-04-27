from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, session, url_for
import os
import time

from definitions import (
    close_db,
    DB_URI,
    init_engine,
    init_session_factory,
    PROD_MAP,
    STRIPE_PUBLISHABLE_KEY,
    )
from models import Base
from routers.stripe import stripe_bp
from routers.users import user_bp
from services.user_service import is_enable_premium_feature, is_enable_ultimate_feature

PRICE_ID_BY_NAME = { PROD_MAP[x]["name"]:PROD_MAP[x]["price_ids"]["monthly"] for x in PROD_MAP }

def create_app(database_url:str = DB_URI):
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    app.register_blueprint(stripe_bp)
    app.register_blueprint(user_bp)

    app.jinja_env.globals["now"] = time.time

    engine = init_engine(database_url)
    SessionLocal = init_session_factory(engine)
    Base.metadata.create_all(bind=engine)
    app.session_factory = SessionLocal

    app.teardown_request(close_db)

    @app.route("/")
    def home():
        return render_template(
           'home.html',
           )

    @app.route("/register/")
    def register():
        if "id" in session:
            return redirect(url_for('dashboard'))
        return render_template(
           'register.html',
           )

    @app.route("/login/", methods=["GET"])
    def login_page():
        if "id" in session:
            return redirect(url_for('dashboard'))
        return render_template(
           'login.html',
        )

    @app.route("/onboarding/", methods=["GET"])
    def onboarding_page():
        if "id" in session:
            if not session["onboarding_completed"]:
                return render_template(
                    'onboarding.html',
                    prod_map = PRICE_ID_BY_NAME,
                    STRIPE_PUBLISHABLE_KEY=STRIPE_PUBLISHABLE_KEY,
                )
            return redirect(url_for('dashboard'))
        return redirect(url_for('login_page'))

    @app.route("/dashboard/")
    def dashboard():
        if "id" in session:
            if not session["onboarding_completed"]:
                return redirect(url_for('onboarding_page'))
            return render_template(
                'dashboard.html',
                is_premium_feature = is_enable_premium_feature(session["id"]),
                is_ultimate_feature = is_enable_ultimate_feature(session["id"])
        )
        else:
            return redirect(url_for('login_page'))


    @app.route("/dashboard/premium-feature/")
    def premium_feature():
        if "id" in session:
            unix_now = time.time()
            if (
                is_enable_premium_feature(session["id"]) and
                unix_now < session["current_period_end"]
            ):
                return render_template(
                    'premium-feature.html',
                    is_premium_feature = True,
                    is_ultimate_feature = is_enable_ultimate_feature(session["id"])
                )
            else:
                return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login_page'))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
