"""ASGI shim for deployments that invoke ``uvicorn server:app``.

This keeps compatibility whether the working directory is the repo root
or the ``backend`` subfolder.
"""

from backend.main import app

__all__ = ["app"]
