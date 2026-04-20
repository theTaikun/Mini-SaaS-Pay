from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, session, url_for
import os
import time

from definitions import close_db, DB_URI, init_engine, init_session_factory, STRIPE_PUBLISHABLE_KEY, STRIPE_RECURRING_PRICE_ID
from models import Base
from routers.stripe import stripe_bp
from routers.users import user_bp

load_dotenv()

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
                    price_id=STRIPE_RECURRING_PRICE_ID,
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
                price_id=STRIPE_RECURRING_PRICE_ID,
        )
        else:
            return redirect(url_for('login_page'))


    @app.route("/dashboard/premium-feature/")
    def premium_feature():
        if "id" in session:
            unix_now = time.time()
            if (
                session["price_id"] == STRIPE_RECURRING_PRICE_ID
                and unix_now < session["current_period_end"]
            ):
                return render_template(
                    'premium-feature.html',
                    price_id=STRIPE_RECURRING_PRICE_ID,
                )
            else:
                return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login_page'))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
