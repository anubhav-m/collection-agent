"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Request

from app.core.settings import Settings, get_settings
from app.db.mongo import MongoDatabase

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_mongo(request: Request) -> MongoDatabase:
    return request.app.state.mongo


MongoDep = Annotated[MongoDatabase, Depends(get_mongo)]
