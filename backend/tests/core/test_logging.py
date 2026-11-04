import json
import logging

from app.core.context import conversation_id_var, request_id_var
from app.core.logging import JsonFormatter


def test_formatter_emits_json_with_context_and_extras():
    record = logging.makeLogRecord(
        {"name": "t", "levelname": "INFO", "msg": "hello %s", "args": ("x",), "tokens": 5}
    )
    r_token = request_id_var.set("req-1")
    c_token = conversation_id_var.set("conv-9")
    try:
        payload = json.loads(JsonFormatter().format(record))
    finally:
        request_id_var.reset(r_token)
        conversation_id_var.reset(c_token)
    assert payload["msg"] == "hello x"
    assert payload["request_id"] == "req-1"
    assert payload["conversation_id"] == "conv-9"
    assert payload["tokens"] == 5
    assert "args" not in payload
