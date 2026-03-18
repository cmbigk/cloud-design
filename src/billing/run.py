"""
Main entry point for the Billing service.
Starts the Flask API and the background RabbitMQ worker.
"""

import threading
from app import app
from app.worker import start_worker
from waitress import serve


if __name__ == "__main__":
    # --- OPTION 1: WIDE MODE (API + Worker) ---
    print(" [*] Starting Billing Service in WIDE mode (API + Worker)...")
    # Start the RabbitMQ worker in a background thread
    worker_thread = threading.Thread(target=start_worker, daemon=True)
    worker_thread.start()

    # Start the Flask API
    print(" [*] Starting Billing API on port 8080...")
    serve(app, host="0.0.0.0", port=8080)

    # --- OPTION 2: NARROW MODE (Worker Only) ---
    # To use narrow mode, comment out OPTION 1 and uncomment below:
    # print(" [*] Starting Billing Service in NARROW mode (Worker only)...")
    # start_worker()
