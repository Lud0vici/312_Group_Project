from urllib.parse import parse_qs, unquote
import string

def extract_credentials(request):
    body = request.body.decode()
    parsed_body = parse_qs(body)

    username = parsed_body.get('username', [''])[0]
    password = parsed_body.get('password', [''])[0]

    password = unquote(password)

    credentials = [username, password]

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