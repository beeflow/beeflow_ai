# Beeflow AI Toolkit

A lightweight Python toolkit providing:
- an OpenAI Chat Completions client (with simple dependency injection),
- prompt builders (e.g., concise feedback for a poker session),
- a JSON Schema validator (Draft-07),
- a registry and a base class for content generators.

Distributed under the MIT licence. Suitable for use in any project.

## Installation

Option A: install directly from the source directory (recommended for local development)

```bash
# Optional: create and activate a virtual environment
uv venv .venv && source .venv/bin/activate

# Install the package
uv sync
```

Option B: build and install from a wheel package

```bash
# Build the artefacts
uv run --with build python -m build

# Install the wheel (optional)
# Prefer using `uv sync` for local development; wheel install is usually
# needed only for consumers. If you still want to validate the wheel,
# create a temporary project and add it as a dependency, then sync.
# Example:
#   mkdir /tmp/wheel-check && cd /tmp/wheel-check
#   uv init
#   uv add ../path/to/dist/beeflow_ai_toolkit-*.whl
#   uv sync
```

Requirements: Python 3.11+, `openai>=1.40.0`, `jsonschema>=4.21.0` (installed automatically).

## Building the package

You can build both source distribution (sdist) and wheel using the standard Python build tool.

```bash
# Optional: clean previous build artefacts
rm -rf dist/

# Build sdist and wheel according to pyproject.toml
uv run --with build python -m build

# The artefacts will be placed in ./dist/
ls dist/
# beeflow_ai_toolkit-<version>.tar.gz (sdist)
# beeflow_ai_toolkit-<version>-py3-none-any.whl (wheel)

# Optionally, validate the wheel in a throwaway project:
#   mkdir /tmp/wheel-check && cd /tmp/wheel-check
#   uv init
#   uv add ../path/to/dist/beeflow_ai_toolkit-*.whl
#   uv sync
```

The project is configured via `pyproject.toml` and uses `setuptools` as the build backend.

## Publishing to TestPyPI/PyPI

Before publishing, ensure `pyproject.toml` contains correct metadata (`name`, `version`, `description`, `authors`, `readme`, `licence`, `dependencies`). Increment `version` for every release.

1) Build the artefacts (sdist + wheel):

```bash
uv run --with build python -m build
```

2) Install Twine and check the distributions:

```bash
uv run --with twine twine check dist/*
```

3) Upload to TestPyPI first (recommended):

```bash
uv run --with twine twine upload --repository testpypi dist/*
# Username: __token__
# Password: <your TestPyPI token>
```

Verify installation from TestPyPI in a clean environment:

```bash
uv venv .venv-test && source .venv-test/bin/activate
uv add --index-url https://test.pypi.org/simple \
  --extra-index-url https://pypi.org/simple \
  beeflow-ai-toolkit
uv sync
```

4) Upload to PyPI (production):

```bash
uv run --with twine twine upload dist/*
# Username: __token__
# Password: <your PyPI token>
```

You can also set environment variables to avoid interactive prompts:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<your-token>
uv run --with twine twine upload dist/*
```

Optional: add `classifiers` and `project.urls` to `pyproject.toml` to improve your package’s visibility on PyPI.

## Quick Start

### 1) OpenAI client and poker feedback generator

```python
from beeflow_ai import (
    OpenAIChatCompletionClient,
    PokerFeedbackGenerator,
    PokerStats,
)

# Set the API key (or pass it explicitly to the client)
# export OPENAI_API_KEY=...

client = OpenAIChatCompletionClient()  # uses OPENAI_API_KEY from the environment

# Optional: select the model via an environment variable, e.g. POKER_FEEDBACK_MODEL
# export POKER_FEEDBACK_MODEL=gpt-4o-mini

gen = PokerFeedbackGenerator(chat_completion_client=client)  # default model from env or 'gpt-5'
stats: PokerStats = {
    "hands_played": 120,
    "vpip": 28.3,
    "pfr": 22.1,
    "three_bet": 9.6,
    "aggression_factor": 2.7,
    "showdown_win_rate": 55.0,
    "net_profit_bb": 35,
    "session_minutes": 75,
    "strengths": ["Value-betting"],
    "leaks": ["Calling 3-bets too wide"],
}
text = gen.generate(stats, top_p=0.8, max_tokens=64)
print(text)
```

### 2) JSON Schema validation

```python
from beeflow_ai import JsonSchemaValidator, SchemaValidatorLoader

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0},
    },
    "required": ["name"],
}
validator = JsonSchemaValidator(schema)
result = validator.validate({"name": "Alice", "age": 8})
assert result["ok"]

# Or use the loader (e.g., when schemas are packaged as data files)
loader = SchemaValidatorLoader(
    schema_pkg="my.schemas",
    schema_name="person.schema.json",
)
print(loader.validate({"name": "Bob"}))
```

## Public API

The package exports:
- `OpenAIChatCompletionClient`, `ChatCompletionClient` (protocol),
- `BaseContentGenerator`, `ContentGeneratorRegistry`, `register_content_generator`,
- `PokerFeedbackPromptBuilder`, `PokerFeedbackGenerator`, `PokerStats`,
- `JsonSchemaValidator`, `SchemaValidatorLoader`, `load_schema`.

Internal implementations rely on relative imports and dependency injection, making them easy
to test without patching global modules.

## Environment Configuration

- `OPENAI_API_KEY` — API key for OpenAI.
- `STORY_GENERATION_MODEL` — default model for generators based on `BaseContentGenerator`.
- `POKER_FEEDBACK_MODEL` — default model used by `PokerFeedbackGenerator`.

## Licence

MIT — see the `LICENSE` file for details.
