import logging
from abc import ABC, abstractmethod
from functools import lru_cache

from groq import APIConnectionError, APIStatusError, Groq, RateLimitError

from app.core.config import settings
from app.core.exceptions import LLMUnavailableError

logger = logging.getLogger("roh.llm")


class LLMClient(ABC):
    """What the rest of the app needs from any language model."""

    @abstractmethod
    def generate(self, messages: list[dict]) -> str:
        """Send chat messages to a model and return the reply text."""


class GroqLLMClient(LLMClient):
    def __init__(self):
        self._client: Groq | None = None

    def _get_client(self) -> Groq:
        if not settings.groq_api_key:
            raise LLMUnavailableError("The AI service is not configured.")
        if self._client is None:
            self._client = Groq(
                api_key=settings.groq_api_key,
                timeout=settings.llm_timeout_seconds,
                max_retries=1,
            )
        return self._client

    def generate(self, messages: list[dict]) -> str:
        client = self._get_client()
        try:
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                temperature=0.3,
                max_tokens=settings.llm_max_tokens,
            )
        except RateLimitError:
            logger.warning("Groq rate limit reached")
            raise LLMUnavailableError("Roh is busy right now. Please try again in a moment.")
        except APIConnectionError:
            logger.exception("Could not reach Groq")
            raise LLMUnavailableError("Roh could not reach the AI service. Please try again.")
        except APIStatusError as exc:
            logger.error("Groq returned status %s: %s", exc.status_code, exc.message)
            raise LLMUnavailableError("Roh is temporarily unavailable. Please try again.")

        text = response.choices[0].message.content
        if not text:
            raise LLMUnavailableError("Roh could not produce an answer. Please try again.")
        return text.strip()


@lru_cache
def get_llm_client() -> LLMClient:
    return GroqLLMClient()