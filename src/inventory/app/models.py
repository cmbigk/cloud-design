"""
Database models for the Inventory service.

This module defines the SQLAlchemy models used to represent
the inventory data, specifically the Movie table.
"""

from app import db


class Movie(db.Model):
    """Movie model for storing movie details."""

    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        """Return movie details as a dictionary."""
        return {"id": self.id, "title": self.title, "description": self.description}
