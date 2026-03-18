"""
Billing service application initialization.
Configures Flask, SQLAlchemy, and registers routes.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure Database
DB_HOST = os.environ.get("DB_HOST", "billing-db")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", os.environ.get("USER", "postgres"))
DB_PASS = os.environ.get("DB_PASS", "")
DB_NAME = os.environ.get("DB_NAME", "orders_db")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Import models and routes AFTER db is defined to avoid circular imports
from . import models, routes  # noqa: F401

with app.app_context():
    db.create_all()
