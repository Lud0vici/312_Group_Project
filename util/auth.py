def extract_credentials(request):
    body = request.body.decode()
    username = ''
    password = ''

    split_by_body = body.split('&')
    for credential in split_by_body:
        split_by_credential = credential.split('=')
        key = split_by_credential[0]
        value = split_by_credential[1]
        if key == 'username':
            username = value
        elif key == 'password':
            password = value

    password = password.replace('%21', '!')
    password = password.replace('%40', '@')
    password = password.replace('%23', '#')
    password = password.replace('%24', '$')
    password = password.replace('%5E', '^')
    password = password.replace('%26', '&')
    password = password.replace('%28', '(')
    password = password.replace('%29', ')')
    password = password.replace('%2D', '-')
    password = password.replace('%5F', '_')
    password = password.replace('%3D', '=')
    password = password.replace('%25', '%')

    credentials = [username, password]
    return credentials

def validate_password(password):
    if len(password) < 8:
        return False
    
    if not any(c.islower() for c in password):
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='} for c in password):
        return False
    
    valid_characters = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+")
    if any(c not in valid_characters for c in password):
        return False

    return True