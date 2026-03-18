"""
Main entry point for the Gateway service.
Runs the Flask application using Waitress WSGI server.
"""
from app import app

from waitress import serve

if __name__ == "__main__":
    app.logger.info("Starting Gateway with Waitress on port 3000")
    serve(app, host="0.0.0.0", port=3000)
