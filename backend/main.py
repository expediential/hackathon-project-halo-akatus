"""Convenience ASGI entrypoint: uvicorn main:app --app-dir backend."""
from app.main import app

__all__ = ["app"]
