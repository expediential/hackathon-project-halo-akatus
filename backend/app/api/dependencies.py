"""Shared dependencies; authentication can add a role resolver here later."""
from app.db.database import get_db

__all__ = ["get_db"]
