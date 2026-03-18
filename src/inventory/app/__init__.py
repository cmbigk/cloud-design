"""
Flask application initialization for the Inventory service.
Configures the database connection and model/route registration.
"""

import os


from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure Database
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", os.environ.get("USER", "postgres"))
DB_PASS = os.environ.get("DB_PASS", "")
DB_NAME = os.environ.get("DB_NAME", "movies_db")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Import models and routes to register them with SQLAlchemy and Flask.
# These are imported at the bottom to avoid circular dependencies.
from app import models, routes  # noqa: F401

# Initialize database tables
with app.app_context():
    db.create_all()
