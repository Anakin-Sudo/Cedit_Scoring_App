"""
SQLAlchemy models for the credit scoring service.

Currently the app logs each prediction request along with the inputs,
predicted class and probability.  The table is called `request_logs`.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, Text
from sqlalchemy.types import JSON

from .database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    input_data = Column(JSON, nullable=False)
    prediction = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)

    def __repr__(self) -> str:
        return (
            f"RequestLog(id={self.id}, timestamp={self.timestamp},"
            f" prediction={self.prediction}, probability={self.probability})"
        )