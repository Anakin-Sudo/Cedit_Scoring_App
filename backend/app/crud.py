"""
CRUD helper functions for database interactions.

At the moment only insertion is implemented.  Additional functions could be
added to query logs for monitoring or audit purposes.
"""

from sqlalchemy.orm import Session
from .models import RequestLog


def create_log_entry(
    db: Session,
    features: dict,
    prediction: int,
    probability: float,
) -> RequestLog:
    """Persist a new request log entry to the database."""
    log = RequestLog(
        input_data=features,
        prediction=prediction,
        probability=probability,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log