"""File-backed development cache for LLM responses. Off unless enabled."""

import asyncio
import hashlib
import json
from pathlib import Path

from app.llm.types import LLMRequest, LLMResponse


class ResponseCache:
    def __init__(self, directory: Path, enabled: bool) -> None:
        self.directory = directory
        self.enabled = enabled

    @staticmethod
    def key(model: str, request: LLMRequest) -> str:
        raw = json.dumps([model, request.model_dump(mode="json")], sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    async def get(self, key: str) -> LLMResponse | None:
        if not self.enabled:
            return None
        path = self.directory / f"{key}.json"
        text = await asyncio.to_thread(_read_if_exists, path)
        return LLMResponse.model_validate_json(text) if text else None

    async def put(self, key: str, response: LLMResponse) -> None:
        if not self.enabled:
            return
        path = self.directory / f"{key}.json"
        await asyncio.to_thread(_write, path, response.model_dump_json())


def _read_if_exists(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.exists() else None


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
