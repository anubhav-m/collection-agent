import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def make(**values: str) -> Settings:
    values.setdefault("mongodb_uri", "mongodb+srv://placeholder.invalid")
    return Settings(_env_file=None, **values)


def test_keys_are_in_fallback_order_and_blanks_skipped():
    settings = make(gemini_api_key_1="k1", gemini_api_key_2="  ", gemini_api_key_3="k3")
    assert settings.gemini_api_keys == ["k1", "k3"]


def test_no_keys_gives_empty_list():
    assert make().gemini_api_keys == []


def test_secrets_are_hidden_in_repr():
    settings = make(gemini_api_key_1="super-secret", mongodb_uri="mongodb://user:pw@host")
    text = repr(settings)
    assert "super-secret" not in text
    assert "pw@host" not in text


def test_missing_mongodb_uri_fails(monkeypatch):
    monkeypatch.delenv("MONGODB_URI", raising=False)
    with pytest.raises(ValidationError, match="mongodb_uri"):
        Settings(_env_file=None)
