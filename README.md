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
python -m pip install .
```

Option B: build and install from a wheel package

```bash
python -m pip install -U build && python -m build
python -m pip install dist/beeflow_ai_toolkit-*.whl
```

Requirements: Python 3.11+, `openai>=1.40.0`, `jsonschema>=4.21.0` (installed automatically).

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
