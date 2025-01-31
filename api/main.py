from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from pymongo import MongoClient
import pika
import json
import logging
from models import User
from services import save_to_mongo, send_to_rabbitmq

app = FastAPI()

# Configuração do MongoDB
client = MongoClient("mongo:27017")
db = client.user_db

# Configuração do RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='user_queue')

# Configuração de Logs
logging.basicConfig(filename='logs/app.log', level=logging.INFO)

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(None),  # Recebe o arquivo JSON (opcional)
    json_data: str = Body(None)     # Recebe o JSON diretamente no body (opcional)
):
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