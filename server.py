import base64
import os
import secrets
import socketserver
import uuid

# import socketio as socketio
from flask import Flask, send_from_directory, request, redirect, url_for, make_response, jsonify, render_template, \
    session, send_file
from flask_sock import Sock
from util import database_handler
from util import auth
from util.database_handler import user_collection
import hashlib
from datetime import datetime, timedelta
import json
import base64
from werkzeug.utils import secure_filename
# from flask_socketio import SocketIO, emit

connected_clients = []

app = Flask(__name__, template_folder="src")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
sock = Sock(app)
#socketio = SocketIO(app, cors_allowed_origins="*")


def add_no_sniff(response):
    response.headers["X-Content-Type-Options"] = "nosniff"


@app.route("/")
def serve_login_page():
    response = send_from_directory('src', 'LoginPage.html')
    add_no_sniff(response)
    return response


@app.route("/RegistrationPage.html")
def serve_registration_page():
    response = send_from_directory("src", "RegistrationPage.html")
    add_no_sniff(response)
    return response


@app.route("/functions.js")
def serve_javascript():
    response = send_from_directory("public", "functions.js")
    add_no_sniff(response)
    return response


@app.route("/homepage_functions.js")
def serve_homepage_js():
    response = send_from_directory("public", "homepage_functions.js")
    add_no_sniff(response)
    return response


@app.route("/login-registration.css")
def serve_css():
    response = send_from_directory("public", "login-registration.css")
    add_no_sniff(response)
    return response


@app.route("/rocket_ball.png")
def serve_rocket_ball():
    response = send_from_directory("public", "image/rocket_ball.png")
    add_no_sniff(response)
    return response

@app.route('/public/image_water/<path:filename>')
def serve_water_file(filename):
    return send_from_directory('public/image_water', filename)

# Route for serving files from /public/image_fire
@app.route('/public/image_fire/<path:filename>')
def serve_fire_file(filename):
    return send_from_directory('public/image_fire', filename)

# Route for serving files from /public/image_grass
@app.route('/public/image_grass/<path:filename>')
def serve_grass_file(filename):
    return send_from_directory('public/image_grass', filename)

# Route for listing filenames in /public/image_water directory
@app.route('/public/image_water')
def list_water_files():
    directory = 'public/image_water'
    files = os.listdir(directory)
    return jsonify(files)

# Route for listing filenames in /public/image_fire directory
@app.route('/public/image_fire')
def list_fire_files():
    directory = 'public/image_fire'
    files = os.listdir(directory)
    return jsonify(files)

# Route for listing filenames in /public/image_grass directory
@app.route('/public/image_grass')
def list_grass_files():
    directory = 'public/image_grass'
    files = os.listdir(directory)
    return jsonify(files)

# edit function so that it calls on insertUser to put into database
@app.route("/register", methods=['POST'])
def serve_registration():
    user_credentials = auth.extract_credentials(request)
    # assumed that user_credentials returns ["first", "last", "email", "username", "pass", "confirmed-pass"]
    first_name = user_credentials[0]
    last_name = user_credentials[1]
    email = user_credentials[2]
    username = user_credentials[3]
    password = user_credentials[4]
    confirmedPassword = user_credentials[5]
    validPassword = auth.validate_password(password)
    user_data = user_collection.find_one({"username": username})  # error
    user_email = user_collection.find_one({"email": email})
    if user_data is not None:
        response = make_response("Username already taken!")
        add_no_sniff(response)
        response.status_code = 404
        return response
    elif auth.validate_username(username) is False:
        response = make_response("Username is invalid!")
        add_no_sniff(response)
        response.status_code = 404
        return response
    elif user_email is not None:
        response = make_response("Email is associated with an account!")
        add_no_sniff(response)
        response.status_code = 404
        return response
    elif validPassword != True:
        response = make_response("Password does not meet requirements!")
        add_no_sniff(response)
        response.status_code = 404
        return response
    elif password != confirmedPassword:
        response = make_response("Passwords do not match!")
        add_no_sniff(response)
        response.status_code = 404
        return response
    else:
        salt, hashed_password = database_handler.salt_and_hash_password(password)
        database_handler.insert_user(first_name, last_name, email, username, salt, hashed_password)
        print(database_handler.user_collection.find_one({"username": username})["username"])
        return redirect(url_for("serve_login_page"))


@app.route("/login", methods=["POST"])
def serve_login():
    user_credentials = auth.extract_credentials(request)
    # assumed that user_credentials returns ["first", "last", "email", "username", "pass", "confirmed-pass"]
    username = user_credentials[3]
    password = user_credentials[4]
    user_data = database_handler.user_collection.find_one({"username": username})
    if user_data is None:
        response = make_response("User not found")
        add_no_sniff(response)
        response.status_code = 404
        return response
    else:
        salt = user_data["salt"]
        salted_password = password + salt
        curr_user_password = hashlib.sha256(salted_password.encode()).hexdigest()
        if curr_user_password == user_data["password"]:  # if password matches the one found in the user_collection db
            session["username"] = username
            token = secrets.token_urlsafe(32)
            hashed_token = hashlib.sha256(token.encode()).hexdigest()
            database_handler.user_collection.update_one({"username": username}, {"$set": {"auth_token": hashed_token}})
            response = redirect(url_for('serve_homepage'))  # make a response with an empty body
            expire_date = datetime.now()
            expire_date = expire_date + timedelta(minutes=60)
            response.set_cookie("authentication-token", token, httponly=True, expires=expire_date,
                                max_age=3600)  # set auth-token cookie
            session['username'] = username
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=60)
            session.modified = True
            return response
        else:
            response = make_response("Incorrect password")
            add_no_sniff(response)
            response.status_code = 404
            return response


@app.route("/homepage")
def serve_homepage():
    username = session.get("username")
    auth_token = request.cookies.get("authentication-token")

    if not username or not auth_token:
        # If username or authentication token is not found, return 404
        response = make_response("User data or authentication token is not found.")
        add_no_sniff(response)
        response.status_code = 404
        return response

    hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
    user_data = user_collection.find_one({"username": username, "auth_token": hashed_token})

    if not user_data:  # Auth token stored in database doesn't match with auth token stored on webpage
        response = make_response(
            "Authentication token is incorrect. Please re-enter the correct authentication token and refresh the page.")
        add_no_sniff(response)
        response.status_code = 404
        return response

    with open("src/HomePage.html", "rb") as file:
        file_contents = file.read()
    file_contents = file_contents.replace(b"{{user}}", username.encode())
    response = make_response(file_contents)
    add_no_sniff(response)
    return response


@app.route("/logout", methods=["POST"])
def serve_logout():  # serve logout button when we have the user on our actual page, not login or registration
    auth_token = request.cookies.get("authentication-token", None)
    response = redirect(url_for('serve_login_page'))
    add_no_sniff(response)
    if auth_token is not None:
        response.delete_cookie('authentication-token')
        hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
        user_data = user_collection.find_one({"auth_token": hashed_token})
        username = user_data["username"]  # why giving None?
        user_collection.update_one({"username": username}, {"$set": {"auth_token": ""}})
        session.clear()
        response.delete_cookie("session")
    return response



def reserved_char_decode(char):
    char = char.upper()
    if char == "%20":
        return " "
    elif char == "%3A":
        return ":"
    elif char == "%2F":
        return "/"
    elif char == "%3F":
        return "?"
    elif char == "%23":
        return "#"
    elif char == "%58":
        return "["
    elif char == "%5D":
        return "]"
    elif char == "%40":
        return "@"
    elif char == "%21":
        return "!"
    elif char == "%24":
        return "$"
    elif char == "%26":
        return "&"
    elif char == "%27":
        return "'"
    elif char == "%28":
        return "("
    elif char == "%29":
        return ")"
    elif char == "%2A":
        return "*"
    elif char == "%2B":
        return "+"
    elif char == "%2C":
        return ","
    elif char == "%3B":
        return ";"
    elif char == "%3D":
        return "="

def full_char_decoder(message):
    message = str(message)

    index = 0
    hex_char = ""
    decoded_msg = ""

    while index < len(message):
        char = message[index]
        if char == "%":
            hex_char += char + message[index + 1] + message[index + 2]
            hex_char = hex_char.upper()
            decoded_char = reserved_char_decode(hex_char)
            decoded_msg += decoded_char
            index += 3
        else:
            decoded_msg += message[index]
            index += 1
    return decoded_msg


def escape_HTML(message):
    char_dict = {}
    char_dict["&"] = "&amp;"
    char_dict["<"] = "&lt;"
    char_dict[">"] = "&gt;"
    char_dict['"'] = "&quot"
    char_dict["'"] = "&#39"

    new_safe_message = ""

    for char in message:
        if char in char_dict:
            new_safe_message += char_dict[char]
        else:
            new_safe_message += char

    return new_safe_message

@app.route("/chat-messages", methods=["POST"])
def create_chat_message():
    username = session.get("username")
    auth_token = request.cookies.get("authentication-token")

    if not username or not auth_token:
        # If username or authentication token is not found, return 404
        response = make_response("User data or authentication token is not found.")
        add_no_sniff(response)
        response.status_code = 404
        return response
    # message_content = request.form.get("message")
    data = json.loads(request.data)

    # char decode
    # escape html

    message_content = full_char_decoder(data["message"])
    message_content = escape_HTML(message_content)


    if not message_content:
        response = make_response("Message is empty")
        add_no_sniff(response)
        response.status_code = 404
        return response

    database_handler.insert_chat_message(username, message_content)

    response = make_response(message_content)
    # response.status_code = 200
    return response


@app.route("/chat-messages", methods=["GET"])
def get_chat_messages():
    chat_messages = database_handler.chat_collection.find({})
    chat_history = []
    for data in chat_messages:
        message = data["message"]
        username = data["username"]
        msg_id = data["id"]
        chat_entry = {"message": message, "username": username, "id": msg_id}
        chat_history.append(chat_entry)
    chat_history_json = json.dumps(chat_history)
    response = make_response(chat_history_json)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route("/homepageStyle.css")
def serve_homepage_css():
    response = send_from_directory("public", "homepageStyle.css")
    add_no_sniff(response)
    return response

@app.route("/profile.css")
def serve_profile_css():
    response = send_from_directory("public", "profile.css")
    add_no_sniff(response)
    return response

def save_image(filepath, data):
    with open(filepath, 'wb') as f:
        f.write(data)

@app.route("/upload", methods=["POST"])
def file_uploads():
    username = session.get("username")


    file = request.files['file']
    # data = file.read()


    message = ""
    post_content = request.form.get('post_content', '')

    if file:
        data = file.read()
        if data.startswith(b"\xff\xd8") or data.startswith(b"\xFF\xD8"):    # jpeg
            filename = str(uuid.uuid4()) + ".jpg"
            directory_path = "public/image/"
            file_path = directory_path + filename
            save_image(file_path, data)
            message = f'<img src="http://localhost:8080/public/image/{filename}" type="image/jpeg" alt="{filename}" class="my_image"/> <br> {post_content}'

        if data.startswith(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A") or data.startswith(b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"):
            filename = str(uuid.uuid4()) + ".png"  # filename could easily use uuid for
            directory_path = "public/image/"
            file_path = directory_path + filename  # path is correct
            save_image(file_path, data)
            message = f'<img src="http://localhost:8080/public/image/{filename}" type="image/png" alt="{filename}" class="my_image"/> <br> {post_content}'

        if data.startswith(b"\x47\x49\x46\x38\x37\x61") or data.startswith(b"\x47\x49\x46\x38\x39\x61"):
            filename = str(uuid.uuid4()) + ".gif"  # filename could easily use uuid for
            directory_path = "public/image/"
            file_path = directory_path + filename  # path is correct
            save_image(file_path, data)
            message = f'<img src="http://localhost:8080/public/image/{filename}" type="image/gif" alt="{filename}" class="my_image"/> <br> {post_content}'

        mp4_file_signature = data[:8]
        if mp4_file_signature.endswith(b"ftyp"):
            # elif file_type == "mp4":
            filename = str(uuid.uuid4()) + ".mp4"
            directory_path = "public/image/"
            file_path = directory_path + filename
            save_image(file_path, data)
            message = f'<video width="400" controls autoplay muted><source src="http://localhost:8080/public/image/{filename}" type="video/mp4"> alt="{filename}</video> <br> {post_content}'

        if data.startswith(b"\x49\x44\x33"):
            filename = str(uuid.uuid4()) + ".mp3"
            directory_path = "public/image/"
            file_path = directory_path + filename
            save_image(file_path, data)
            message = f'<audio controls><source src="http://localhost:8080/public/image/{filename}" type="audio/mpeg"> alt="{filename}</audio> <br> {post_content}'
    else:
        message = post_content

    message_id = str(uuid.uuid4())
    database_handler.chat_collection.insert_one({"messageType": "chatMessage", "username": username, "message": message, "id": message_id})

    return redirect(url_for('serve_homepage'))

    # response = make_response(message)
    # response.status_code = 200
    # add_no_sniff(response)
    # return response
    # return jsonify({'message': 'File uploaded successfully'})






@app.route("/public/image/<filename>", methods=["GET"])
def file_serve(filename):
    sanitized_filename = secure_filename(filename)

    file_path = os.path.join("./public/image/", sanitized_filename)

    if os.path.exists(file_path) is False:
        response = make_response("Image does not exist")
        add_no_sniff(response)
        response.status_code = 404
        return response
    else:
        response_content_type = "application/octet-stream"

        if sanitized_filename.endswith("jpg") or sanitized_filename.endswith("jpeg"):
            response_content_type = "image/jpeg"
        elif sanitized_filename.endswith("png"):
            response_content_type = "image/png"
        elif sanitized_filename.endswith("gif"):
            response_content_type = "image/gif"
        elif sanitized_filename.endswith("mp4"):
            response_content_type = "video/mpeg"
        elif sanitized_filename.endswith("mp3"):
            response_content_type = "audio/mpeg"

        return send_file(file_path, mimetype=response_content_type)


@app.route("/insert_image_icon.png")
def serve_image_icon_png():
    response = send_from_directory("public", "image/insert_image_icon.png")
    add_no_sniff(response)
    return response

@sock.route('/public/image/<filename>')
def serve_image(filename):
    # send_from_directory('public/image', filename)
    response_content_type = "image/jpeg"
    sanitized_filename = secure_filename(filename)

    file_path = os.path.join("./public/image/", sanitized_filename)
    return send_file(file_path, mimetype=response_content_type)


@sock.route('/websocket')
def websocket(ws):
    connected_clients.append(ws)  # Add the client to the set of connected clients

    username = session.get("username")
    try:
        while True:
            message = ws.receive()
            if message is not None:  # Check if a message is received
                data = json.loads(message)
                message_type = data["messageType"]
                user_message = ""

                if message_type == "chatMessage":
                    user_message = escape_HTML(data["message"])

                elif message_type == "image":           # Images only, without any message
                    image_data = data["image"]
                    byte_data = base64.b64decode(image_data.split(",")[1])

                    if image_data:
                        if byte_data.startswith(b"\xff\xd8") or byte_data.startswith(b"\xFF\xD8"):
                            filename = str(uuid.uuid4()) + ".jpg"
                            directory_path = "public/image/"
                            file_path = directory_path + filename
                            save_image(file_path, byte_data)
                            user_message = f'<img src="http://localhost:8080/public/image/{filename}" type="image/jpeg" alt="{filename}" class="my_image"/>'

                        if byte_data.startswith(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A") or byte_data.startswith(b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"):
                            filename = str(uuid.uuid4()) + ".png"
                            directory_path = "public/image/"
                            file_path = directory_path + filename
                            save_image(file_path, byte_data)
                            user_message = f'<img src="http://localhost:8080/public/image/{filename}" type="image/png" alt="{filename}" class="my_image"/>'

                        if byte_data.startswith(b"\x47\x49\x46\x38\x37\x61") or byte_data.startswith(b"\x47\x49\x46\x38\x39\x61"):
                            filename = str(uuid.uuid4()) + ".gif" 
                            directory_path = "public/image/"
                            file_path = directory_path + filename
                            save_image(file_path, byte_data)
                            user_message = f'<img src="http://localhost:8080/public/image/{filename}" type="image/gif" alt="{filename}" class="my_image"/>'

                        mp4_file_signature = byte_data[:8]
                        if mp4_file_signature.endswith(b"ftyp"):
                            filename = str(uuid.uuid4()) + ".mp4"
                            directory_path = "public/image/"
                            file_path = directory_path + filename
                            save_image(file_path, byte_data)
                            user_message = f'<video width="400" controls autoplay muted><source src="http://localhost:8080/public/image/{filename}" type="video/mp4"> alt="{filename}</video>'

                        if byte_data.startswith(b"\x49\x44\x33"):
                            filename = str(uuid.uuid4()) + ".mp3"
                            directory_path = "public/image/"
                            file_path = directory_path + filename
                            save_image(file_path, byte_data)
                            user_message = f'<audio controls><source src="http://localhost:8080/public/image/{filename}" type="audio/mpeg"> alt="{filename}</audio> <br>'

                elif message_type == "imageText":
                    message_data = data["message"]
                    image_data = data["image"]
                    byte_data = base64.b64decode(image_data.split(",")[1])

                    if image_data:
                        if byte_data.startswith(b"\xff\xd8") or byte_data.startswith(b"\xFF\xD8"):
                            filename = str(uuid.uuid4()) + ".jpg"
                            directory_path = "public/image/"
                            file_path = directory_path + filename
                            save_image(file_path, byte_data)
                            user_message = f'<img src="http://localhost:8080/public/image/{filename}" type="image/jpeg" alt="{filename}" class="my_image"/> <br> {message_data}'

                        if byte_data.startswith(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A") or byte_data.startswith(b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"):
                            filename = str(uuid.uuid4()) + ".png"
                            directory_path = "public/image/"
                            file_path = directory_path + filename
                            save_image(file_path, byte_data)
                            user_message = f'<img src="http://localhost:8080/public/image/{filename}" type="image/png" alt="{filename}" class="my_image"/> <br> {message_data}'

                        if byte_data.startswith(b"\x47\x49\x46\x38\x37\x61") or byte_data.startswith(b"\x47\x49\x46\x38\x39\x61"):
                            filename = str(uuid.uuid4()) + ".gif"
                            directory_path = "public/image/"
                            file_path = directory_path + filename
                            save_image(file_path, byte_data)
                            user_message = f'<img src="http://localhost:8080/public/image/{filename}" type="image/gif" alt="{filename}" class="my_image"/> <br> {message_data}'

                        mp4_file_signature = byte_data[:8]
                        if mp4_file_signature.endswith(b"ftyp"):
                            filename = str(uuid.uuid4()) + ".mp4"
                            directory_path = "public/image/"
                            file_path = directory_path + filename
                            save_image(file_path, byte_data)
                            user_message = f'<video width="400" controls autoplay muted><source src="http://localhost:8080/public/image/{filename}" type="video/mp4"> alt="{filename}</video> <br> {message_data}'

                        if byte_data.startswith(b"\x49\x44\x33"):
                            filename = str(uuid.uuid4()) + ".mp3"
                            directory_path = "public/image/"
                            file_path = directory_path + filename
                            save_image(file_path, byte_data)
                            user_message = f'<audio controls><source src="http://localhost:8080/public/image/{filename}" type="audio/mpeg"> alt="{filename}</audio> <br> {message_data}'

                message_id = str(uuid.uuid4())
                constructed_message = {
                    "messageType": data["messageType"],
                    "username": str(username),
                    "message": user_message,
                    "id": message_id
                }

                # how to serve images, and images+text???
                database_handler.chat_collection.insert_one({
                    "messageType": data["messageType"],
                    "username": username,
                    "message": user_message,
                    "id": message_id
                })

                constructed_message = json.dumps(constructed_message)
                for client in connected_clients:
                    client.send(constructed_message)
    finally:
        connected_clients.remove(ws)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
    # socketio.run(app, host='0.0.0.0', port=8080, debug=True)
