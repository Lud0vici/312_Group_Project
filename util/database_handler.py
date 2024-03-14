from pymongo import MongoClient 

mongo_client =  MongoClient("TeamRocketMongo")
db = mongo_client["TeamRocketDB"] 
user_collection = db["users"]  #hold the user information 
chat_collection = db["chat"]   #collection for chat 

#checks if user already exists and adds username + salt + hash into database 

def insert_user(username: str, salt: str, hashedPassword: str): 
    if user_collection.find_one({"username": username}): 
        raise Exception("Username already exists.") 
    user_collection.insert_one({
        "username": username ,  
        "salt" : salt ,
        "password" : hashedPassword 
        }) 



