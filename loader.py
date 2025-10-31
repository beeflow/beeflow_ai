from __future__ import annotations

import json
from importlib import resources
from typing import Any, Dict

# Keep validators decoupled from I/O; this loader just fetches schema dicts.


def load_schema(package: str, name: str) -> Dict[str, Any]:
    """
    Load a JSON schema bundled as package data.
    Example: load_schema('schemas.student_worksheets', 'student-worksheet.schema.v1.json')
    """
    with resources.files(package).joinpath(name).open("r", encoding="utf-8") as f:
        return json.load(f)