from flask import Flask

# Flask app
flask_app = Flask(__name__)

# Route to display Hello World
@flask_app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=80)
