"""
Billing worker module.

This module consumes order messages from RabbitMQ and persists
the billing data into the PostgreSQL database using the Flask-SQLAlchemy model.
"""

import os
import time
import json
import sys
import pika
from sqlalchemy.exc import SQLAlchemyError
from app import app, db
from app.models import Order

# RabbitMQ Configuration
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "guest")
QUEUE_NAME = "billing_queue"


def process_message(ch, method, _properties, body):
    """
    Callback function that processes incoming messages from RabbitMQ.
    """
    with app.app_context():
        try:
            data = json.loads(body)
            print(f" [x] Received order: {data}")
            
            new_order = Order(
                user_id=data.get("user_id"),
                number_of_items=data.get("number_of_items"),
                total_amount=data.get("total_amount"),
            )
            db.session.add(new_order)
            db.session.commit()
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except json.JSONDecodeError as e:
            print(f" [!] JSON Decode Error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except SQLAlchemyError as e:
            print(f" [!] Database Error: {e}")
            db.session.rollback()
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            print(f" [!] Unexpected Error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            raise e


def start_worker():
    """
    Establishes a connection to RabbitMQ and starts consuming messages.
    """
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)

    connection = None
    for _ in range(20):
        try:
            connection = pika.BlockingConnection(params)
            break
        except pika.exceptions.AMQPConnectionError:
            print(" [!] RabbitMQ not available, retrying in 5s...")
            time.sleep(5)

    if not connection:
        print(" [!] Could not connect to RabbitMQ. Exiting.")
        sys.exit(1)

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message)
    print(" [*] Billing Worker waiting for messages...")
    channel.start_consuming()
