"""
API routes for the Billing service.
"""

from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from app import app, db
from app.models import Order


@app.route("/bills", methods=["GET"])
def get_all_bills():
    """Returns a list of all billing orders."""
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders]), 200


@app.route("/bills", methods=["DELETE"])
def delete_all_bills():
    """Deletes all billing orders."""
    try:
        num_deleted = db.session.query(Order).delete()
        db.session.commit()
        return jsonify({"message": f"Deleted {num_deleted} orders"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error while deleting bills", "details": str(e)}), 500


@app.route("/bills/<int:bill_id>", methods=["DELETE"])
def delete_bill(bill_id):
    """Deletes a specific billing order by ID."""
    order = Order.query.get(bill_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    try:
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": f"Order {bill_id} deleted"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error while deleting bill {bill_id}", "details": str(e)}), 500
