# Beeflow AI Toolkit

Lekka biblioteka Pythona zawierająca:
- klienta do OpenAI Chat Completions (z prostym DI),
- budowniczych promptów (np. krótka informacja zwrotna dla sesji pokera),
- walidator JSON Schema (Draft-07),
- rejestr i bazową klasę generatora treści.

Biblioteka jest dostarczana na licencji MIT i może być użyta w dowolnym projekcie.

## Instalacja

Wariant A: instalacja bezpośrednio z folderu (zalecane dla lokalnego użytku)

```bash
cd whn_application/beeflow_ai
python -m pip install .
```

Wariant B: budowa i instalacja z paczki (wheel)

```bash
cd whn_application/beeflow_ai
python -m pip install build && python -m build
python -m pip install dist/beeflow_ai_toolkit-*.whl
```

Wymagania: Python 3.11+, `openai>=1.40.0`, `jsonschema>=4.21.0` (instalują się automatycznie).

## Szybki start

### 1) Klient OpenAI i generator informacji zwrotnej do pokera

```python
from beeflow_ai import OpenAIChatCompletionClient, PokerFeedbackGenerator, PokerStats

# Ustaw klucz API (lub przekaż jawnie do klienta)
# export OPENAI_API_KEY=...  # lub ustaw w kodzie

client = OpenAIChatCompletionClient()  # użyje OPENAI_API_KEY z env

# Opcjonalnie: wybór modelu z ENV, np. POKER_FEEDBACK_MODEL
# export POKER_FEEDBACK_MODEL=gpt-4o-mini

gen = PokerFeedbackGenerator(chat_completion_client=client)  # domyślny model z env lub 'gpt-5'
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

### 2) Walidacja JSON Schema

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

# Lub z loaderem (np. pliki schematów jako data w pakiecie)
loader = SchemaValidatorLoader(schema_pkg="my.schemas", schema_name="person.schema.json")
print(loader.validate({"name": "Bob"}))
```

## API publiczne

Pakiet eksportuje:
- `OpenAIChatCompletionClient`, `ChatCompletionClient` (protokół),
- `BaseContentGenerator`, `ContentGeneratorRegistry`, `register_content_generator`,
- `PokerFeedbackPromptBuilder`, `PokerFeedbackGenerator`, `PokerStats`,
- `JsonSchemaValidator`, `SchemaValidatorLoader`, `load_schema`.

Wewnętrzne implementacje używają importów relatywnych i DI, dzięki czemu łatwo je testować
bez patchowania modułów globalnych.

## Konfiguracja środowiska

- `OPENAI_API_KEY` — klucz API do OpenAI.
- `STORY_GENERATION_MODEL` — domyślny model dla generatorów bazujących na `BaseContentGenerator`.
- `POKER_FEEDBACK_MODEL` — domyślny model używany przez `PokerFeedbackGenerator`.

## Licencja

MIT — szczegóły w pliku `LICENSE`.
