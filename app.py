from flask import Flask, render_template

# Flask app
flask_app = Flask(__name__)

# Flask route to render the UI
@flask_app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=80)
