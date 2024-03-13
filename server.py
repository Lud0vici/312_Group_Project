import socketserver
from flask import Flask, send_from_directory

app = Flask(__name__)


@app.route("/")
def serve_login_page():
    return send_from_directory('src', 'LoginPage.html')

@app.route("/functions.js")
def serve_javascript():
    return send_from_directory("public", "functions.js")

@app.route("/style.css")
def serve_css():
    return send_from_directory("public", "style.css")

@app.route("/rocket_ball.png")
def serve_rocket_ball():
    return send_from_directory("public", "image/rocket_ball.png")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
    # app.run()
    # comment for demo
