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
       price_id=os.getenv("STRIPE_RECURRING_PRICE_ID"),
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
        s = dict(session)
        return render_template(
            'dashboard.html',
        data=s
    )
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
