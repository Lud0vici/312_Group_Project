import secrets
import socketserver
from flask import Flask, send_from_directory, request, redirect, url_for, flash, make_response
from util import database_handler
from util import auth
import hashlib


app = Flask(__name__)

def add_no_sniff(response):
    response.headers["X-Content-Type-Options"] = "nosniff"

@app.route("/")
def serve_login_page():
    response = send_from_directory('src', 'LoginPage.html')
    add_no_sniff(response)
    return response

@app.route("/functions.js")
def serve_javascript():
    response = send_from_directory("public", "functions.js")
    add_no_sniff(response)
    return response

@app.route("/style.css")
def serve_css():
    response = send_from_directory("public", "style.css")
    add_no_sniff(response)
    return response

@app.route("/rocket_ball.png")
def serve_rocket_ball():
    response = send_from_directory("public", "image/rocket_ball.png")
    add_no_sniff(response)
    return response

#edit function so that it calls on insertUser to put into database 
@app.route("/register", methods=['POST'])
def serve_registration():
    first_name = request.form.get('first-name')
    last_name = request.form.get('last-name') 
    email = request.form.get('email')
    username = request.form.get('username') 
    password = request.form.get('password')
    confirmedPassword = request.form.get('confirm-password')
    if password != confirmedPassword: 
        #the flash functio is from Flask which just displays a temp message 
        flash("Passwords do not match") 
        return redirect(url_for("registration_form")) #need to adjust regist.... 
    salt, hashed_password = database_handler.salt_and_hash_password(password)
    try: 
        database_handler.insert_user(username, salt, hashed_password)       # fix it with all parameters first_name: str, last_name: str, email: str, username: str, salt: str, hashedPassword: str
    except Exception as e: #try if else statments instead of try and except 
        flash(str(e))
        return redirect(url_for("serve_login_page")) #need to adjust serve... 


    # response = send_from_directory("public", "/register")
    # add_no_sniff(response)
    # return response

@app.route("/login", methods=["POST"])
def serve_login():
    user_credentials = auth.extract_credentials(request)

    # assumed that user_credentials returns ["first", "last", "email", "username", "pass", "confirmed-pass"]

    username = user_credentials[3]
    password = user_credentials[4]

    user_data = database_handler.user_collection.find_one({"username": username})


    if user_data is None:   #if user not found in db, flash "User not found"
        flash("User not found")
    else:   #if user is found, we now have to check the password
        salt = user_data["salt"]
        salted_password = password + salt
        curr_user_password = hashlib.sha256(salted_password.encode()).hexdigest()

        if curr_user_password == user_data["password"]:     #if password matches the one found in the user_collection db
            token = secrets.token_urlsafe(32)
            hashed_token = hashlib.sha256(token.encode()).hexdigest()
            database_handler.user_collection.update_one({"username": username}, {"$set": {"auth_token": hashed_token}})
            response = make_response()
            response.set_cookie("authentication-token", token, httponly=True, ex)

    pass

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)