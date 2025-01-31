from fastapi import FastAPI, HTTPException, File, UploadFile, Body
from pymongo import MongoClient
import pika
import json
import logging
import mysql.connector
from mysql.connector import Error
from typing import List
from pydantic import BaseModel

app = FastAPI()

# Configuração do MongoDB
client = MongoClient("mongodb://mongo:27017")
db = client.user_db

# Configuração do RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='user_queue')

# Configuração de Logs
logging.basicConfig(filename='logs/app.log', level=logging.INFO)

# Modelo de dados do usuário
class User(BaseModel):
    name: str
    email: str
    age: int

# Endpoint para upload de arquivo JSON
@app.post("/upload/")
async def upload_file(file: UploadFile = File(None), json_data: str = Body(None)):
    try:
        # Verifica se o JSON foi enviado via arquivo ou diretamente no body
        if file:
            contents = await file.read()
            users = json.loads(contents)
        elif json_data:
            users = json.loads(json_data)
        else:
            raise HTTPException(status_code=400, detail="Nenhum JSON fornecido.")

        # Persiste os dados no MongoDB
        mongo_id = save_to_mongo(db, users)

        # Envia uma mensagem para o RabbitMQ
        send_to_rabbitmq(channel, mongo_id)

        logging.info(f"JSON recebido e processado: {mongo_id}")
        return {"message": "JSON recebido e está sendo processado", "id": mongo_id}
    except json.JSONDecodeError:
        logging.error("Erro ao decodificar o JSON.")
        raise HTTPException(status_code=400, detail="JSON inválido.")
    except Exception as e:
        logging.error(f"Erro ao processar o JSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para retornar todos os dados armazenados no MySQL
@app.get("/users/", response_model=List[User])
def get_all_users():
    try:
        # Conecta ao MySQL
        connection = mysql.connector.connect(
            host='mysql',
            database='users_db',
            user='user',
            password='password'
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT name, email, age FROM users")
            users = cursor.fetchall()
            return users
    except Error as e:
        logging.error(f"Erro ao buscar dados no MySQL: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao buscar dados no MySQL.")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Funções auxiliares
def save_to_mongo(db, users):
    result = db.uploads.insert_many(users)
    return str(result.inserted_ids[0])

def send_to_rabbitmq(channel, mongo_id):
    channel.basic_publish(exchange='', routing_key='user_queue', body=mongo_id)