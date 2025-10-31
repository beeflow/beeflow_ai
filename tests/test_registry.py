from __future__ import annotations

from typing import Optional

from beeflow_ai.openai_chat_completition_client import (
    BaseContentGenerator,
    register_content_generator,
    ContentGeneratorRegistry,
)


class DummyBuilder:
    def build(self) -> str:
        return "prompt"


class DummyClient:
    def create(
        self,
        *,
        model_name: str,
        messages,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
    ) -> str:
        return "ok"


class DummyGenerator(BaseContentGenerator):
    def __init__(self, model_name: str = "dummy") -> None:
        super().__init__(
            prompt_builder=DummyBuilder(),
            chat_completion_client=DummyClient(),
            schema_validator=None,
            model_name=model_name,
        )

    def generate(self, *args, **kwargs) -> str:
        return "generated"


def test_content_generator_registry_register_get_available_clear():
    ContentGeneratorRegistry.clear()
    gen_a = DummyGenerator(model_name="model-a")
    ContentGeneratorRegistry.register(gen_a)

    assert ContentGeneratorRegistry.get("model-a") is gen_a
    assert "model-a" in ContentGeneratorRegistry.available_models()

    ContentGeneratorRegistry.clear()
    assert ContentGeneratorRegistry.get("model-a") is None


def test_register_content_generator_decorator_registers_by_model_name():
    ContentGeneratorRegistry.clear()

    @register_content_generator
    def make_gen(name: str) -> DummyGenerator:
        return DummyGenerator(model_name=name)

    gen_b = make_gen("model-b")
    assert ContentGeneratorRegistry.get("model-b") is gen_b