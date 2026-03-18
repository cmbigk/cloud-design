"""
Gateway routes module.
Handles proxying requests to the inventory service and publishing to the billing queue.
"""

import os

import json
import requests
import pika
from flask import request, jsonify
from app import app

INVENTORY_URL = os.environ.get("INVENTORY_URL", "http://inventory-app:5001")
BILLING_URL = os.environ.get("BILLING_URL", "http://billing-app:8080")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "guest")
QUEUE_NAME = "billing_queue"


@app.route("/api/movies", methods=["GET", "POST", "DELETE"], strict_slashes=False)
def proxy_movies():
    """
    Proxy movie list requests to the inventory service.
    Supports GET (list), POST (create), and DELETE (delete all).
    """

    app.logger.info(f"Incoming {request.method} request to /api/movies")
    try:
        if request.method == "GET":
            resp = requests.get(f"{INVENTORY_URL}/movies", params=request.args)
            return jsonify(resp.json()), resp.status_code

        if request.method == "POST":
            resp = requests.post(f"{INVENTORY_URL}/movies", json=request.get_json())
            return jsonify(resp.json()), resp.status_code

        if request.method == "DELETE":
            resp = requests.delete(f"{INVENTORY_URL}/movies")
            return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Inventory service unavailable: {e}")
        return (
            jsonify({"error": "Inventory service unavailable", "details": str(e)}),
            503,
        )


@app.route(
    "/api/movies/<int:movie_id>", methods=["GET", "PUT", "DELETE"], strict_slashes=False
)
def proxy_movie(movie_id):
    """
    Proxy single movie requests to the inventory service by ID.
    Supports GET (detail), PUT (update), and DELETE (delete).
    """

    try:
        if request.method == "GET":
            resp = requests.get(f"{INVENTORY_URL}/movies/{movie_id}")
            return jsonify(resp.json()), resp.status_code
        if request.method == "PUT":
            resp = requests.put(
                f"{INVENTORY_URL}/movies/{movie_id}", json=request.get_json()
            )
            return jsonify(resp.json()), resp.status_code
        if request.method == "DELETE":
            resp = requests.delete(f"{INVENTORY_URL}/movies/{movie_id}")
            return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        return (
            jsonify({"error": "Inventory service unavailable", "details": str(e)}),
            503,
        )


@app.route("/api/billing", methods=["POST"], strict_slashes=False)
def manage_billing():
    """
    Manage billing orders.
    POST: Publish message to RabbitMQ
    """

    if request.method == "POST":
        data = request.get_json()
        if not data or not all(
            k in data for k in ("user_id", "number_of_items", "total_amount")
        ):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            publish_to_billing(data)
            return jsonify({"message": "Order submitted to billing queue"}), 200
        except pika.exceptions.AMQPError as e:
            app.logger.error(f"Failed to publish to RabbitMQ: {e}")
            return jsonify({"error": "Billing service queue unavailable"}), 503
        except Exception as e:
            app.logger.error(f"Unexpected error in billing publish: {e}")
            raise e


def publish_to_billing(order_data):
    """
    Publishes order data to the RabbitMQ billing queue.
    """

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(order_data),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()


# Extra routes for inspecting and editing billing database


@app.route("/api/billing", methods=["GET", "DELETE"], strict_slashes=False)
def manage_billing_extra():
    """
    Manage billing orders.
    GET: Fetch all bills from Billing API.
    DELETE: Delete all bills via Billing API.
    """
    try:
        if request.method == "GET":
            resp = requests.get(f"{BILLING_URL}/bills")
            return jsonify(resp.json()), resp.status_code

        if request.method == "DELETE":
            resp = requests.delete(f"{BILLING_URL}/bills")
            return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Billing service API unavailable: {e}")
        return (
            jsonify({"error": "Billing service API unavailable", "details": str(e)}),
            503,
        )


@app.route("/api/billing/<int:bill_id>", methods=["DELETE"], strict_slashes=False)
def delete_billing_order(bill_id):
    """
    Delete a specific billing order by ID via the Billing API.
    """
    try:
        resp = requests.delete(f"{BILLING_URL}/bills/{bill_id}")
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Billing service API unavailable: {e}")
        return (
            jsonify({"error": "Billing service API unavailable", "details": str(e)}),
            503,
        )
