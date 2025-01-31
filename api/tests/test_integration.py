import pytest
import json
import pika
import pymongo
import mysql.connector
from mysql.connector import Error
from fastapi.testclient import TestClient
from main import app

# Configuração do cliente de teste FastAPI
client = TestClient(app)

# Fixture para conectar ao MongoDB
@pytest.fixture(scope="module")
def mongo_client():
    client = pymongo.MongoClient("mongo:27017")
    yield client
    client.close()

# Fixture para conectar ao RabbitMQ
@pytest.fixture(scope="module")
def rabbitmq_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='user_queue')
    yield channel
    connection.close()

# Fixture para conectar ao MySQL
@pytest.fixture(scope="module")
def mysql_connection():
    try:
        connection = mysql.connector.connect(
            host='mysql',
            database='users_db',
            user='user',
            password='password'
        )
        yield connection
    finally:
        if connection.is_connected():
            connection.close()

# Fixture para limpar os dados após cada teste
@pytest.fixture(autouse=True)
def cleanup(mongo_client, mysql_connection):
    yield
    # Limpa o MongoDB
    db = mongo_client.user_db
    db.uploads.delete_many({})
    # Limpa o MySQL
    cursor = mysql_connection.cursor()
    cursor.execute("DELETE FROM users")
    mysql_connection.commit()
    cursor.close()

# Teste de upload de arquivo JSON e persistência no MongoDB
def test_upload_and_mongo_persistence(mongo_client):
    # Dados de exemplo
    test_data = [
        {"name": "João Silva", "email": "joao.silva@example.com", "age": 30},
        {"name": "Maria Oliveira", "email": "maria.oliveira@example.com", "age": 25}
    ]
    test_file = ("test.json", json.dumps(test_data).encode(), "application/json")

    # Faz o upload do arquivo
    response = client.post("/upload/", files={"file": test_file})
    assert response.status_code == 200
    mongo_id = response.json()["id"]

    # Verifica se os dados foram persistidos no MongoDB
    db = mongo_client.user_db
    collection = db.uploads
    result = collection.find_one({"_id": pymongo.ObjectId(mongo_id)})
    assert result is not None
    assert result["name"] == "João Silva"
    assert result["email"] == "joao.silva@example.com"
    assert result["age"] == 30

# Teste de envio de mensagem para o RabbitMQ
def test_rabbitmq_message(rabbitmq_channel, mongo_client):
    # Dados de exemplo
    test_data = [
        {"name": "Carlos Souza", "email": "carlos.souza@example.com", "age": 40}
    ]
    test_file = ("test.json", json.dumps(test_data).encode(), "application/json")

    # Faz o upload do arquivo
    response = client.post("/upload/", files={"file": test_file})
    assert response.status_code == 200
    mongo_id = response.json()["id"]

    # Verifica se a mensagem foi enviada para o RabbitMQ
    method_frame, header_frame, body = rabbitmq_channel.basic_get(queue='user_queue', auto_ack=True)
    assert body.decode() == mongo_id

# Teste de processamento assíncrono e persistência no MySQL
def test_mysql_persistence(mysql_connection, rabbitmq_channel, mongo_client):
    # Dados de exemplo
    test_data = [
        {"name": "Ana Costa", "email": "ana.costa@example.com", "age": 35}
    ]
    test_file = ("test.json", json.dumps(test_data).encode(), "application/json")

    # Faz o upload do arquivo
    response = client.post("/upload/", files={"file": test_file})
    assert response.status_code == 200
    mongo_id = response.json()["id"]

    # Simula o consumo da mensagem pelo RabbitMQ
    method_frame, header_frame, body = rabbitmq_channel.basic_get(queue='user_queue', auto_ack=True)
    assert body.decode() == mongo_id

    # Verifica se os dados foram persistidos no MySQL
    cursor = mysql_connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = 'ana.costa@example.com'")
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == "Ana Costa"  # name
    assert result[2] == "ana.costa@example.com"  # email
    assert result[3] == 35  # age
    cursor.close()

# Teste de envio de JSON via body e persistência no MongoDB
def test_upload_json_body_and_mongo_persistence(mongo_client):
    # Dados de exemplo
    test_data = [
        {"name": "Pedro Alves", "email": "pedro.alves@example.com", "age": 28}
    ]

    # Envia o JSON diretamente no body
    response = client.post("/upload/", json=test_data)
    assert response.status_code == 200
    mongo_id = response.json()["id"]

    # Verifica se os dados foram persistidos no MongoDB
    db = mongo_client.user_db
    collection = db.uploads
    result = collection.find_one({"_id": pymongo.ObjectId(mongo_id)})
    assert result is not None
    assert result["name"] == "Pedro Alves"
    assert result["email"] == "pedro.alves@example.com"
    assert result["age"] == 28

# Teste de erro quando nenhum JSON é fornecido
def test_upload_no_data():
    response = client.post("/upload/")
    assert response.status_code == 400
    assert "Nenhum JSON fornecido" in response.json()["detail"]