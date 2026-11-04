from app.agent.history import MAX_USER_TURNS, to_messages
from app.db.records import ConversationEvent as Event
from app.db.records import EventKind as K
from app.llm.types import Role


def ev(kind: K, **fields) -> Event:
    return Event(conversation_id="c", kind=kind, **fields)


def test_tool_results_for_one_reply_are_grouped():
    calls = [{"name": "a", "args": {}, "call_id": "1", "signature": b"sig"}, {"name": "b"}]
    events = [
        ev(K.USER, text="hi"),
        ev(K.TOOL_CALL, tool_calls=calls),
        ev(K.TOOL_RESULT, tool_name="a", call_id="1", result={"ok": True}),
        ev(K.TOOL_RESULT, tool_name="b", result={"ok": False}),
        ev(K.ESCALATION, reason="dispute"),
        ev(K.ASSISTANT, text="done"),
    ]
    messages = to_messages(events)
    assert [m.role for m in messages] == [Role.USER, Role.MODEL, Role.TOOL, Role.MODEL]
    assert messages[1].tool_calls[0].signature == b"sig"
    assert [r.name for r in messages[2].tool_results] == ["a", "b"]


def test_only_recent_turns_are_sent():
    events = [e for i in range(10) for e in (ev(K.USER, text=f"u{i}"), ev(K.ASSISTANT, text="ok"))]
    messages = to_messages(events)
    assert len(messages) == MAX_USER_TURNS * 2 and messages[0].text == "u4"
