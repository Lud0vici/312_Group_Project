import socketserver
from flask import Flask, send_from_directory

app = Flask(__name__)


@app.route("/")
def serve_login_page():
    return send_from_directory('src', 'LoginPage.html')

@app.route("/functions.js")
def serve_javascript():
    return send_from_directory("public", "index.js")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
    # app.run()
    # comment for demo
