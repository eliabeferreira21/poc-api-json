import pika
import json
import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(filename='logs/app.log', level=logging.INFO)

def process_message(ch, method, properties, body):
    mongo_id = body.decode()
    logging.info(f"Processing message: {mongo_id}")

    try:
        connection = mysql.connector.connect(
            host='mysql',
            database='users_db',
            user='user',
            password='password'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            # Aqui você deve buscar os dados do MongoDB e inserir no MySQL
            # Exemplo: cursor.execute("INSERT INTO users (name, email, age) VALUES (%s, %s, %s)", (name, email, age))
            connection.commit()
            logging.info(f"Data inserted into MySQL: {mongo_id}")
    except Error as e:
        logging.error(f"Error inserting into MySQL: {str(e)}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='user_queue')
    channel.basic_consume(queue='user_queue', on_message_callback=process_message, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()