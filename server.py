import secrets
import socketserver
from flask import Flask, send_from_directory, request, redirect, url_for, make_response, jsonify, render_template, session
from util import database_handler
from util import auth
from util.database_handler import user_collection
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="src")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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
    user_data = user_collection.find_one({"username": username})   #error
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
        if curr_user_password == user_data["password"]:     #if password matches the one found in the user_collection db
            session["username"] = username
            token = secrets.token_urlsafe(32)
            hashed_token = hashlib.sha256(token.encode()).hexdigest()
            database_handler.user_collection.update_one({"username": username}, {"$set": {"auth_token": hashed_token}})
            response = redirect(url_for('serve_homepage'))      #make a response with an empty body
            expire_date = datetime.now()
            expire_date = expire_date + timedelta(minutes=60)
            response.set_cookie("authentication-token", token, httponly=True, expires=expire_date, max_age=3600)     #set auth-token cookie
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

    if not user_data: # Auth token stored in database doesn't match with auth token stored on webpage
        response = make_response("Authentication token is incorrect. Please re-enter the correct authentication token and refresh the page.")
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
def serve_logout():     #serve logout button when we have the user on our actual page, not login or registration
    auth_token = request.cookies.get("authentication-token", None)
    response = redirect(url_for('serve_login_page'))
    add_no_sniff(response)
    if auth_token is not None:
        response.delete_cookie('authentication-token')
        hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
        user_data = user_collection.find_one({"auth_token": hashed_token})
        username = user_data["username"]    #why giving None?
        user_collection.update_one({"username": username}, {"$set": {"auth_token": ""}})
        session.clear()
        response.delete_cookie("session")
    return response

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
    message_content = request.form.get("message")
    if not message_content: 
        response = make_response("Message is empty") 
        add_no_sniff(response)
        response.status_code = 404
        return response 
    database_handler.insert_chat_message(username, message_content)

    
@app.route("/chat")
def serve_chat(): 
    chat_messages = database_handler.chat_collection.find()
    messages_list = [{"username": msg["username"], "message": msg["message"]} for msg in chat_messages]
    



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)