from dotenv import load_dotenv
from flask import Flask, render_template_string
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


@app.route("/")
def home():
    #return render_template('home.html', user=user_info, pretty=json.dumps(user, indent=2))
    return render_template_string('''
        <h1>Hello World</h1>
        <button>Subscribe</button>
    ''')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
