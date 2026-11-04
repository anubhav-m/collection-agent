r"""Run one scripted conversation against a running server and save a report.

Usage (from backend/, server on port 8000):
    .venv\Scripts\python -m scripts.live_chat happy
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

import httpx

from scripts.live_scenarios import SCENARIOS

REPORTS = Path(__file__).resolve().parents[2] / "docs" / "reports"


async def run(name: str, base_url: str) -> dict:
    scenario = SCENARIOS[name]
    turns, conversation_id = [], None
    async with httpx.AsyncClient(base_url=base_url, timeout=180) as client:
        for message in scenario["messages"]:
            body = {"message": message, "conversation_id": conversation_id}
            if conversation_id is None:
                body["lender_id"] = scenario["lender_id"]
            started = time.perf_counter()
            response = await client.post("/chat", json=body)
            response.raise_for_status()
            reply = response.json()
            conversation_id = reply["conversation_id"]
            elapsed = round((time.perf_counter() - started) * 1000)
            turns.append({"user": message, "response": reply, "latency_ms": elapsed})
            print(f"> {message}\n< [{reply['outcome']}] {reply['reply']}\n")
        stored = (await client.get(f"/conversations/{conversation_id}")).json()
    return {"scenario": name, "turns": turns, "stored_conversation": stored}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=sorted(SCENARIOS))
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    report = asyncio.run(run(args.scenario, args.base_url))
    path = REPORTS / f"session2_live_{args.scenario}.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"saved {path.name}")


if __name__ == "__main__":
    main()
