import secrets
import socketserver
from flask import Flask, send_from_directory, request, redirect, url_for, flash, make_response, jsonify, render_template
from util import database_handler
from util import auth
from util.database_handler import user_collection
import hashlib
import datetime



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
    user_credentials = auth.extract_credentials(request)

    # assumed that user_credentials returns ["first", "last", "email", "username", "pass", "confirmed-pass"]
    first_name = user_credentials[0]
    last_name = user_credentials[1]
    email = user_credentials[2]
    username = user_credentials[3]
    #print(username)
    password = user_credentials[4]
    confirmedPassword = user_credentials[5]
    # print("before auth validate")
    validPassword = auth.validate_password(password)
    # print("checking database")
    user_data = user_collection.find_one({"username": username})   #error
    user_email = user_collection.find_one({"email": email})
    if user_data is not None:       #needs more testing when login and homepage are created
        # flash("Username already taken!")
        response = make_response("Username already taken!")
        add_no_sniff(response)
        response.status_code = 404
        #return redirect(url_for('serve_registration_page'))
        return response
        # return render_template("RegistrationPage.html", error_message="Username already taken!")
    elif user_email is not None:
        response = make_response("Email is associated with an account!")
        add_no_sniff(response)
        response.status_code = 404
        # return redirect(url_for('serve_registration_page'))
        return response
    elif validPassword != True:
        # flash("Password does not meet requirements")
        response = make_response("Password does not meet requirements!")
        add_no_sniff(response)
        response.status_code = 404
        #return redirect(url_for('serve_registration_page'))
        return response
        # return render_template("RegistrationPage.html", error_message="Password does not meet requirements")
    elif password != confirmedPassword:
        # flash("Passwords do not match")
        response = make_response("Passwords do not match!")
        add_no_sniff(response)
        response.status_code = 404
        #return redirect(url_for('serve_registration_page'))
        return response
        # return render_template("RegistrationPage.html", error_message="Passwords do not match")
    else:
        salt, hashed_password = database_handler.salt_and_hash_password(password)
        database_handler.insert_user(first_name, last_name, email, username, salt, hashed_password)
        print(database_handler.user_collection.find_one({"username": username})["username"])
        #return redirect("/", code=302)
        return redirect(url_for("serve_login_page"))

        #return redirect(url_for("registration_form")) #need to adjust regist.... 

@app.route("/login", methods=["POST"])
def serve_login():
    user_credentials = auth.extract_credentials(request)

    # assumed that user_credentials returns ["first", "last", "email", "username", "pass", "confirmed-pass"]

    username = user_credentials[3]
    password = user_credentials[4]

    user_data = database_handler.user_collection.find_one({"username": username})


    if user_data is None:   #if user not found in db, flash "User not found"
        flash("User not found")
        response = make_response("User not found")
        add_no_sniff(response)
        response.status_code = 404
        return response
    else:   #if user is found, we now have to check the password
        salt = user_data["salt"]
        salted_password = password + salt
        curr_user_password = hashlib.sha256(salted_password.encode()).hexdigest()

        if curr_user_password == user_data["password"]:     #if password matches the one found in the user_collection db
            token = secrets.token_urlsafe(32)
            hashed_token = hashlib.sha256(token.encode()).hexdigest()
            database_handler.user_collection.update_one({"username": username}, {"$set": {"auth_token": hashed_token}})
            response = redirect(url_for('serve_homepage'))      #make a response with an empty body
            expire_date = datetime.datetime.now()
            expire_date = expire_date + datetime.timedelta(minutes=60)
            response.set_cookie("authentication-token", token, httponly=True, expires=expire_date, max_age=3600)     #set auth-token cookie
            return response
        else:
            flash("Incorrect password")
            response = make_response("Incorrect password")
            add_no_sniff(response)
            response.status_code = 404
            return response

@app.route("/homepage")
def serve_homepage():
    pass

@app.route("/logout")
def serve_logout():     #serve logout button when we have the user on our actual page, not login or registration
    pass


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
