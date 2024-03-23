import secrets
import socketserver
from flask import Flask, send_from_directory, request, redirect, url_for, flash, make_response, render_template
from util import database_handler
from util import auth 
import hashlib

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def add_no_sniff(response):
    response.headers["X-Content-Type-Options"] = "nosniff"

@app.route("/")
def serve_login_page():
    # Access the request object to retrieve the authentication token cookie
    auth_token = request.cookies.get("authentication-token")
    username = "Guest"

    # Now you can use the auth_token to retrieve the username or perform any other actions
    if auth_token:
        user_data = database_handler.user_collection.find_one({"auth_token": auth_token})
        if user_data:
            username = user_data.get("username")
            # You can now use the username or perform any other actions
            # For example, you might render the login page with the username displayed
    
    # Read the HTML file and return its contents as a response
    with open("LoginPage.html", "r") as file:
        html_content = file.read()
    
    # Replace the placeholder with the actual username
    html_content = html_content.replace("{{ username }}", username)

    # Set the Content-Type header to indicate that the response contains HTML
    headers = {"Content-Type": "text/html"}

    # Create a response with the HTML content
    return html_content, 200, headers

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
    password = user_credentials[4]
    confirmedPassword = user_credentials[5]
    validPassword = auth.validate_password(password) 
    user_data = database_handler.user_collection.find_one({"username": username})
    if user_data is not None: 
        flash("Username already taken!")
    if validPassword != True: 
        flash("Password does not meet requirnments") 
    if password == confirmedPassword: 
        salt, hashed_password = database_handler.salt_and_hash_password(password)
        database_handler.insert_user(first_name, last_name, email, username, salt, hashed_password)
    if password != confirmedPassword: 
        flash("Passwords do not match") 
    return redirect("/", code=302)
        #return redirect(url_for("registration_form")) #need to adjust regist.... 
    # try: 
    #     database_handler.insert_user(first_name, last_name, email, username, salt, hashed_password)
    # except Exception as e: #try if else statments instead of try and except 
    #     flash(f"Error during registration: {str(e)}")
    # return redirect(url_for("LoginPage.html"))
        

    # response = send_from_directory("public", "/register")
    # add_no_sniff(response)
    # return response

@app.route("/login", methods=["POST"])
def serve_login():
    # Extract credentials to find user data in user collection
    user_credentials = auth.extract_credentials(request)
    username = user_credentials[3]
    password = user_credentials[4]
    user_data = database_handler.user_collection.find_one({"username": username})

    if user_data is None:
        flash("User not found")
    else:
        salt = user_data["salt"]
        salted_password = password + salt
        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest() # Hashes salted_password

        if hashed_password == user_data["password"]:
            auth_token = secrets.token_urlsafe(32)
            hashed_auth_token = hashlib.sha256(auth_token.encode()).hexdigest()
            database_handler.user_collection.update_one({"username": username}, {"$set": {"auth_token": hashed_auth_token}})
            
            # Serve response that sets the authentication token and redirects to the homepage
            response = redirect("/", code=302)
            response.set_cookie("authentication-token", auth_token, httponly=True, max_age=3600) # Set authentication token
            return response
        else:
            flash("Incorrect password")

    # If user not found or incorrect password, redirect back to login page
    return redirect("/login")

@app.route("/logout")
def serve_logout():     #serve logout button when we have the user on our actual page, not login or registration
    pass


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
