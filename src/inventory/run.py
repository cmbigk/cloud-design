"""
Main entry point for the Inventory service.
Runs the Flask application using Waitress WSGI server.
"""

from app import app

from waitress import serve

if __name__ == "__main__":
    print("Starting Inventory with Waitress on port 8080")
    serve(app, host="0.0.0.0", port=8080)
