from __future__ import annotations

from typing import Any, Dict, List, Type, Callable

from jsonschema import Draft7Validator
from jsonschema.protocols import Validator  # type: ignore[import-not-found]

from .loader import load_schema


class JsonSchemaValidator:
    """Generic JSON Schema validator (draft-07 by default)."""

    def __init__(self, schema: Dict[str, Any], validator_cls: Type[Validator] = Draft7Validator) -> None:
        # Keep responsibility narrow: hold a compiled validator instance.
        self._compiled = validator_cls(schema)

    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a parsed JSON object.

        Returns:
            {"ok": bool, "errors": List[str]}
        """
        errors = sorted(self._compiled.iter_errors(payload), key=lambda e: e.path)
        if not errors:
            return {"ok": True, "errors": []}

        msgs: List[str] = []
        for err in errors:
            # Build a JSONPath-like pointer (readable for humans, simple for logs).
            path = "$"
            for p in err.path:
                path += f"[{p}]" if isinstance(p, int) else f".{p}"
            ctx_lines = [f"- {c.message}" for c in (err.context or [])]
            ctx = "\n    Details:\n    " + "\n    ".join(ctx_lines) if ctx_lines else ""
            msgs.append(f"{path}: {err.message}{ctx}")

        return {"ok": False, "errors": msgs}


class SchemaValidatorLoader(JsonSchemaValidator):
    """
    Load a JSON schema via an injectable loader and initialise a validator.

    This class extends `JsonSchemaValidator` by loading the schema using a provided callable,
    defaulting to the internal `load_schema` utility. This design enables easy testing via
    dependency injection, avoiding the need for patching importlib.resources.

    Attributes:
        schema_pkg (str): The name of the package containing the JSON schema.
        schema_name (str): The name or identifier of the specific schema within the package.
        validator_cls (Type[Validator]): Validator class to use (default: Draft7Validator).
        schema_loader (Callable[[str, str], Dict[str, Any]]): Function to load the schema.
    """

    def __init__(
            self,
            schema_pkg: str,
            schema_name: str,
            validator_cls: Type[Validator] = Draft7Validator,
            schema_loader: Callable[[str, str], Dict[str, Any]] = load_schema,
    ) -> None:
        # Load schema using the provided loader and pass to the base class.
        schema = schema_loader(schema_pkg, schema_name)
        super().__init__(schema=schema, validator_cls=validator_cls)