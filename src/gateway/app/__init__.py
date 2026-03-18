"""
Flask application initialization for the Gateway service.
Defines the application instance and configures logging.
"""

import os

import logging
from flask import Flask

app = Flask(__name__)

# Configure logging
LOD_DIR = "/app/logs"
if not os.path.exists(LOD_DIR):
    os.makedirs(LOD_DIR)

logging.basicConfig(
    filename=f"{LOD_DIR}/gateway.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)
app.logger.setLevel(logging.INFO)

# Import routes at the end to avoid circular imports
from app import routes  # noqa: F401
