from bson import ObjectId
import json

def save_to_mongo(db, users):
    result = db.uploads.insert_many(users)
    return str(result.inserted_ids[0])

def send_to_rabbitmq(channel, mongo_id):
    channel.basic_publish(exchange='', routing_key='user_queue', body=mongo_id)