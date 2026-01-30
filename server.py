from dotenv import load_dotenv
from flask import Flask, redirect, render_template, session, url_for
import os

from routers.stripe import stripe_bp
from routers.users import user_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.register_blueprint(stripe_bp)
app.register_blueprint(user_bp)


STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_RECURRING_PRICE_ID = os.getenv("STRIPE_RECURRING_PRICE_ID")

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
       STRIPE_PUBLISHABLE_KEY=STRIPE_PUBLISHABLE_KEY,
       price_id=STRIPE_RECURRING_PRICE_ID,
       )

@app.route("/login/", methods=["GET"])
def login_page():
    if "id" in session:
        return redirect(url_for('dashboard'))
    return render_template(
       'login.html',
    )

@app.route("/dashboard/")
def dashboard():
    if "id" in session:
        return render_template(
            'dashboard.html',
            price_id=STRIPE_RECURRING_PRICE_ID,
    )
    else:
        return redirect(url_for('login'))


@app.route("/dashboard/premium-feature/")
def premium_feature():
    if "id" in session:
        if session["price_id"] == STRIPE_RECURRING_PRICE_ID:
            return render_template(
                'premium-feature.html',
                price_id=STRIPE_RECURRING_PRICE_ID,
            )
        else:
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login_page'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
