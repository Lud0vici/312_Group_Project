import socketserver
from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route("/")

def serve_index():
    return send_from_directory('public', 'index.html')

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)
  #app.run()
  #comment for demo