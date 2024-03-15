from urllib.parse import unquote_plus
import string

app = Flask(__name__)

def extract_credentials(request):
    first_name = request.form.get('first-name', '')
    last_name = request.form.get('last-name', '')
    email = request.form.get('email', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm-password', '')

    first_name = unquote_plus(first_name)
    last_name = unquote_plus(last_name)
    email = unquote_plus(email)
    username = unquote_plus(username)
    password = unquote_plus(password)
    confirm_password = unquote_plus(confirm_password)

    credentials = [first_name, last_name, email, username, password, confirm_password]

    return credentials

def validate_password(password):
    if len(password) < 12:
        return False
    
    if not any(c.islower() for c in password):
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in string.punctuation for c in password):
        return False
    
    valid_characters = set(string.ascii_letters + string.digits + string.punctuation)
    if any(c not in valid_characters for c in password):
        return False

    return True