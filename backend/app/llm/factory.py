"""Build the real LLM client from settings."""

from google import genai
from google.genai import types

from app.core.settings import Settings
from app.llm.cache import ResponseCache
from app.llm.gemini_client import GeminiClient
from app.llm.pacer import RequestPacer


def build_llm(settings: Settings) -> GeminiClient:
    # attempts=1 disables SDK-level retries so ours are the only retry layer.
    http_options = types.HttpOptions(
        timeout=int(settings.llm_timeout_seconds * 1000),
        retry_options=types.HttpRetryOptions(attempts=1),
    )
    clients = [genai.Client(api_key=k, http_options=http_options) for k in settings.gemini_api_keys]
    return GeminiClient(
        model=settings.gemini_model,
        clients=clients,
        pacer=RequestPacer(settings.llm_requests_per_minute),
        cache=ResponseCache(settings.llm_cache_dir, settings.llm_cache_enabled),
        max_retries=settings.llm_max_retries,
    )
