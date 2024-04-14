from pymongo import MongoClient
import hashlib
import secrets

mongo_client = MongoClient("TeamRocketMongo")
db = mongo_client["TeamRocketDB"] 
user_collection = db["users"]  # database collection containing all users
chat_collection = db["chat"]   # database collection containing all chat messages

#checks if user already exists and adds username + salt + hash into database 

def insert_user(first_name, last_name, email, username, salt, hashedPassword):
    if user_collection.find_one({"username": username}): 
        raise Exception("Username already exists.")
    else:
        user_collection.insert_one({
            "first-name": first_name,
            "last-name": last_name,
            "email": email,
            "username": username,
            "salt": salt,
            "password": hashedPassword,
            "auth_token": ""
            })

def salt_and_hash_password(password):
    salt = secrets.token_hex(16)
    salted_password = password + salt
    salt_hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
    return salt, salt_hashed_password

def insert_chat_message(username, message_content, message_id): 
    message_id = str(uuid.uuid4())
    chat_collection.insert_one({"username": username, "message": message_content, "id": message_id})