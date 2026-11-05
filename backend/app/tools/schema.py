"""Tool argument schemas in the compact form sent to the model."""

from typing import Any

from pydantic import BaseModel


def schema_for(model: type[BaseModel]) -> dict[str, Any]:
    """JSON schema with $refs inlined and titles dropped, to keep the prompt small."""
    schema = model.model_json_schema()
    defs = schema.pop("$defs", {})

    def clean(node: Any) -> Any:
        if isinstance(node, list):
            return [clean(item) for item in node]
        if not isinstance(node, dict):
            return node
        if "$ref" in node:
            return clean(defs[node["$ref"].rsplit("/", 1)[-1]])
        return {k: clean(v) for k, v in node.items() if k != "title"}

    return clean(schema)
