from __future__ import annotations

from typing import Dict, Any

from beeflow_ai.json_schema_validator import (
    JsonSchemaValidator,
    SchemaValidatorLoader,
)


def test_json_schema_validator_ok_and_errors():
    schema: Dict[str, Any] = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0},
        },
        "required": ["name"],
        "additionalProperties": False,
    }

    v = JsonSchemaValidator(schema)
    ok = v.validate({"name": "Alice", "age": 8})
    assert ok["ok"] is True
    assert ok["errors"] == []

    bad = v.validate({"age": -1, "extra": True})
    assert bad["ok"] is False
    # flatten for contains; should include pointer-like paths and messages
    errors = "\n".join(bad["errors"])
    assert "$.name" in errors or "'name' is a required property" in errors
    assert "$.age" in errors or "-1 is less than the minimum of 0" in errors
    assert "$.extra" in errors or "Additional properties are not allowed" in errors


def test_schema_validator_loader_uses_injected_loader():
    def fake_loader(pkg: str, name: str) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"value": {"type": "integer"}},
        }

    v = SchemaValidatorLoader(
        schema_pkg="unused",
        schema_name="unused",
        schema_loader=fake_loader,
    )
    ok = v.validate({"value": 1})
    assert ok["ok"] is True
    bad = v.validate({"value": "x"})
    assert bad["ok"] is False