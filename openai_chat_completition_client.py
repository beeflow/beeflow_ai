from __future__ import annotations

import os
from typing import Optional, Protocol, Callable
from abc import ABC, abstractmethod

import openai
from openai.types.chat import ChatCompletionMessageParam

from .json_schema_validator import JsonSchemaValidator


class PromptBuilder(Protocol):
    def build(self) -> str: ...


class ChatCompletionClient(Protocol):
    """Abstract chat completion client used via dependency injection."""

    def create(
            self,
            *,
            model_name: str,
            messages: list[ChatCompletionMessageParam],
            max_tokens: Optional[int] = None,
            top_p: float = 1.0,
    ) -> str:
        """Return assistant message content (string)."""
        ...


# Minimal protocols to support DI without mocks or patches.
class _HasMessage(Protocol):
    content: Optional[str]


class _HasChoice(Protocol):
    message: _HasMessage


class _HasChoicesResponse(Protocol):
    choices: list[_HasChoice]


class ChatCompletionsCreate(Protocol):
    def __call__(
        self,
        *,
        model: str,
        messages: list[ChatCompletionMessageParam],
        top_p: float,
        max_tokens: Optional[int] = None,
    ) -> _HasChoicesResponse: ...


class OpenAIChatCompletionClient:
    """OpenAI Chat Completions client.

    If no API key is provided, it is read from the environment
    variable "OPENAI_API_KEY". A callable implementing
    ``ChatCompletionsCreate`` may be injected for tests.
    """

    def __init__(
        self,
        api_key: Optional[str] = os.environ.get("OPENAI_API_KEY"),
        openai_create: Optional[ChatCompletionsCreate] = None,
    ) -> None:
        openai.api_key = api_key
        # Dependency injection: allow tests to pass a simple stub instead of
        # patching.
        self._create: ChatCompletionsCreate = (
            openai_create
            or openai.chat.completions.create  # type: ignore[assignment]
        )

    # noinspection PyMethodMayBeStatic
    def create(
            self,
            *,
            model_name: str,
            messages: list[ChatCompletionMessageParam],
            max_tokens: Optional[int] = None,
            top_p: float = 1.0,
    ) -> str:
        # Prepare parameters for OpenAI API call
        api_params = {
            "model": model_name,
            "messages": messages,
            "top_p": top_p,
        }

        # Only include max_tokens if it's not None
        if max_tokens is not None:
            api_params["max_tokens"] = max_tokens

        response = self._create(**api_params)  # type: ignore[arg-type]
        return (response.choices[0].message.content or "").strip()


class BaseContentGenerator(ABC):
    """Base class for generating content via a chat-based model.

    Wires together a ``PromptBuilder``, a ``ChatCompletionClient``, and an
    optional JSON schema validator. Subclasses must implement
    ``generate(...) -> str``.

    Attributes:
        prompt_builder: Builder used to construct prompts.
        chat_completion_client: Client for interacting with the chat model.
        schema_validator: Optional JSON schema validator.
        model_name: Model name; defaults to ``gpt-5`` or
            ``STORY_GENERATION_MODEL`` from environment.
    """

    def __init__(
            self,
            prompt_builder: PromptBuilder,
            chat_completion_client: ChatCompletionClient,
            schema_validator: Optional[JsonSchemaValidator] = None,
            model_name: str = os.environ.get(
                "STORY_GENERATION_MODEL", "gpt-5"
            ),
    ) -> None:
        self.prompt_builder: PromptBuilder = prompt_builder
        self.chat_completion_client: ChatCompletionClient = chat_completion_client
        self.model_name: str = model_name
        self.schema_validator: Optional[JsonSchemaValidator] = schema_validator

    @abstractmethod
    def generate(self, *args: object, **kwargs: object) -> str:
        """Generate content based on provided inputs. Must be implemented by subclasses."""
        raise NotImplementedError


_CONTENT_GENERATORS: dict[str, BaseContentGenerator] = {}


def register_content_generator(func: Callable[..., BaseContentGenerator]):
    def wrapper(*args, **kwargs):
        content_generator = func(*args, **kwargs)
        _CONTENT_GENERATORS[content_generator.model_name] = content_generator
        return content_generator

    return wrapper

 
 
class ContentGeneratorRegistry:
    """In-memory registry of content generators keyed by their model name.

    This registry is intentionally simple and process-local. It allows
    discovering registered generators, retrieving them by model name, and
    clearing the registry in tests. Keeping it separate from the decorator
    aids testability and clarity.
    """

    @staticmethod
    def register(generator: BaseContentGenerator) -> None:
        """Register a generator instance under its `model_name`."""
        _CONTENT_GENERATORS[generator.model_name] = generator

    @staticmethod
    def get(model_name: str) -> Optional[BaseContentGenerator]:
        """Return the generator registered for `model_name`, if any."""
        return _CONTENT_GENERATORS.get(model_name)

    @staticmethod
    def available_models() -> list[str]:
        """Return a sorted list of model names currently registered."""
        return sorted(_CONTENT_GENERATORS.keys())

    @staticmethod
    def clear() -> None:
        """Remove all registered generators (useful in tests)."""
        _CONTENT_GENERATORS.clear()
