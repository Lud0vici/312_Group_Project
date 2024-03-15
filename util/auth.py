import string
from urllib.parse import unquote_plus, unquote
from flask import Flask, request

def extract_credentials(request):
    # Extract form data from Flask request
    first_name = request.form.get('first-name', '')
    last_name = request.form.get('last-name', '')
    email = request.form.get('email', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm-password', '')

    # unquote_plus decodes html-encoded characters
    first_name = unquote_plus(first_name)
    last_name = unquote_plus(last_name)
    email = unquote_plus(email)
    username = unquote_plus(username)
    password = unquote_plus(password)
    confirm_password = unquote_plus(confirm_password)

    return [first_name, last_name, email, username, password, confirm_password]

def validate_password(password):
    if len(password) < 8:
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

def test_extract_credentials1():
    # Simulate form data
    form_data = {
        'first-name': 'John',
        'last-name': 'Doe',
        'email': 'johndoe@example.com',
        'username': 'johndoe',
        'password': 'password123',
        'confirm-password': 'password123'
    }

    # Simulate a Flask request object
    class MockRequest:
        form = form_data

    # Call the extract_credentials function with the mock request object
    actual_credentials = extract_credentials(MockRequest())

    # Decode URL-encoded characters in the expected credentials
    expected_credentials = [unquote_plus(value) for value in form_data.values()]

    # Assert that the actual credentials match the expected credentials
    assert actual_credentials == expected_credentials, f"Expected: {expected_credentials}, Actual: {actual_credentials}"

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    # Call extract_credentials with Flask request
    credentials = extract_credentials(request)
    
    # You can use the credentials as needed here
    print(credentials)

    return 'Registration successful!'

def test_extract_credentials2():
    # Create a Flask test client
    with app.test_client() as client:
        # Simulate a POST request with form data
        response = client.post('/register', data={
            'first-name': 'John',
            'last-name': 'Doe',
            'email': 'johndoe@example.com',
            'username': 'johndoe',
            'password': 'password123',
            'confirm-password': 'password123'
        })

        # Ensure the response indicates successful registration
        assert response.data == b'Registration successful!'

if __name__ == '__main__':
    test_extract_credentials1()
    test_extract_credentials2()