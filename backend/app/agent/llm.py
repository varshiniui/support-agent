import logging
from abc import ABC, abstractmethod
from functools import lru_cache

import groq
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.exceptions import LLMUnavailableError

logger = logging.getLogger("roh.llm")


class LLMClient(ABC):
    """What the rest of the app needs from any language model."""

    @abstractmethod
    def generate(self, messages: list[BaseMessage]) -> str:
        """Send chat messages to a model and return the reply text."""


class GroqLLMClient(LLMClient):
    def __init__(self):
        self._model: ChatGroq | None = None

    def _get_model(self) -> ChatGroq:
        if not settings.groq_api_key:
            raise LLMUnavailableError("The AI service is not configured.")
        if self._model is None:
            self._model = ChatGroq(
                model=settings.llm_model,
                api_key=settings.groq_api_key,
                temperature=0.3,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout_seconds,
                max_retries=1,
            )
        return self._model

    def generate(self, messages: list[BaseMessage]) -> str:
        model = self._get_model()
        try:
            reply = model.invoke(messages)
        except groq.RateLimitError:
            logger.warning("Groq rate limit reached")
            raise LLMUnavailableError("Roh is busy right now. Please try again in a moment.")
        except groq.APIConnectionError:
            logger.exception("Could not reach Groq")
            raise LLMUnavailableError("Roh could not reach the AI service. Please try again.")
        except groq.APIStatusError as exc:
            logger.error("Groq returned status %s: %s", exc.status_code, exc.message)
            raise LLMUnavailableError("Roh is temporarily unavailable. Please try again.")
        except Exception:
            logger.exception("Unexpected LLM error")
            raise LLMUnavailableError("Roh is temporarily unavailable. Please try again.")

        text = reply.content
        if not isinstance(text, str) or not text.strip():
            raise LLMUnavailableError("Roh could not produce an answer. Please try again.")
        return text.strip()


@lru_cache
def get_llm_client() -> LLMClient:
    return GroqLLMClient()