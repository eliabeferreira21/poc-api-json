import pika
import pymongo
import mysql.connector
from mysql.connector import Error
import logging

# Configuração de Logs
logging.basicConfig(filename='logs/app.log', level=logging.INFO)

# Função para processar a mensagem
def process_message(ch, method, properties, body):
    mongo_id = body.decode()
    logging.info(f"Processando mensagem: {mongo_id}")

    try:
        # Conecta ao MongoDB
        mongo_client = pymongo.MongoClient("mongodb://mongo:27017")
        db = mongo_client.user_db
        collection = db.uploads

        # Busca os dados no MongoDB usando o ID da mensagem
        data = collection.find_one({"_id": pymongo.ObjectId(mongo_id)})
        if not data:
            logging.error(f"Dados não encontrados no MongoDB para o ID: {mongo_id}")
            return

        # Conecta ao MySQL
        mysql_connection = mysql.connector.connect(
            host='mysql',
            database='users_db',
            user='user',
            password='password'
        )
        if mysql_connection.is_connected():
            cursor = mysql_connection.cursor()

            # Insere os dados no MySQL
            insert_query = """
                INSERT INTO users (name, email, age)
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (data["name"], data["email"], data["age"]))
            mysql_connection.commit()

            logging.info(f"Dados inseridos no MySQL: {mongo_id}")
    except Error as e:
        logging.error(f"Erro ao inserir no MySQL: {str(e)}")
    except Exception as e:
        logging.error(f"Erro ao processar a mensagem: {str(e)}")
    finally:
        if mysql_connection.is_connected():
            cursor.close()
            mysql_connection.close()

# Função para iniciar o consumidor
def start_consumer():
    try:
        # Conecta ao RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='user_queue')

        # Configura o consumidor
        channel.basic_consume(queue='user_queue', on_message_callback=process_message, auto_ack=True)

        logging.info("Consumidor iniciado. Aguardando mensagens...")
        channel.start_consuming()
    except Exception as e:
        logging.error(f"Erro ao iniciar o consumidor: {str(e)}")

if __name__ == "__main__":
    start_consumer()