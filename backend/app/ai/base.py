from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Implement complete() for any LLM vendor; nothing else in the app knows which one is used."""

    name: str

    @abstractmethod
    async def complete(self, system: str, messages: list[dict], *, max_tokens: int = 500) -> str: ...
