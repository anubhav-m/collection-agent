"""Serve the built React app from the same service, so no CORS setup is needed."""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)


def mount_frontend(app: FastAPI, dist_dir: Path) -> None:
    """Mount last, after the API routes, so API paths always win."""
    if not (dist_dir / "index.html").is_file():
        logger.warning("frontend build not found; serving the API only")
        return
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")
