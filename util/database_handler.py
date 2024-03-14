from pymongo import MongoClient 

mongo_client =  MongoClient("TeamRocketMongo")
db = mongo_client["TeamRocketDB"] 
user_collection = db["users"]  #hold the user information 
chat_collection = db["chat"]   #collection for chat 


