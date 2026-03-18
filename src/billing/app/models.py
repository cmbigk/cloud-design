"""
Database models for the Billing service.
"""

from datetime import datetime
from app import db


class Order(db.Model):
    """
    SQLAlchemy model representing the orders table.
    """

    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    number_of_items = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Return order details as a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "number_of_items": self.number_of_items,
            "total_amount": self.total_amount,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
