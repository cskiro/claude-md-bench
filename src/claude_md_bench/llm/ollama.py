"""
Ollama Client Wrapper

Minimal wrapper for Ollama API calls with error handling, retries, and health checks.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import requests

logger = logging.getLogger(__name__)


@dataclass
class OllamaConfig:
    """Configuration for Ollama client."""

    host: str = "http://localhost:11434"
    model: str = "llama3.2:latest"
    timeout: int = 120
    max_retries: int = 3


class OllamaError(Exception):
    """Base exception for Ollama client errors."""


class OllamaConnectionError(OllamaError):
    """Raised when unable to connect to Ollama server."""


class OllamaTimeoutError(OllamaError):
    """Raised when Ollama request times out."""


class OllamaModelNotFoundError(OllamaError):
    """Raised when the specified model is not available."""


class OllamaClient:
    """Minimal Ollama API client for LLM inference."""

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3.2:latest",
        timeout: int = 120,
        max_retries: int = 3,
    ) -> None:
        """
        Initialize Ollama client.

        Args:
            host: Ollama API endpoint
            model: Model name to use for inference
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts on failure
        """
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.api_url = f"{self.host}/api/generate"

    @classmethod
    def from_config(cls, config: OllamaConfig) -> OllamaClient:
        """Create client from configuration object."""
        return cls(
            host=config.host,
            model=config.model,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text completion from Ollama.

        Args:
            prompt: User prompt
            system: Optional system prompt
            temperature: Sampling temperature (0.0 = deterministic)

        Returns:
            Generated text response

        Raises:
            OllamaConnectionError: If unable to connect to Ollama
            OllamaTimeoutError: If request times out
            OllamaError: For other Ollama-related errors
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        if system:
            payload["system"] = system

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Ollama request (attempt {attempt + 1}/{self.max_retries})")

                response = requests.post(
                    self.api_url,
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                result = response.json()
                generated_text = result.get("response", "").strip()

                if not generated_text:
                    raise OllamaError("Empty response from Ollama")

                logger.debug(f"Ollama generated {len(generated_text)} chars")
                return generated_text

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Ollama connection failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                    continue
                raise OllamaConnectionError(
                    f"Cannot connect to Ollama at {self.host}. "
                    "Ensure Ollama is running: 'ollama serve'"
                ) from e

            except requests.exceptions.Timeout as e:
                logger.warning(f"Ollama request timeout: {e}")
                if attempt < self.max_retries - 1:
                    continue
                raise OllamaTimeoutError(
                    f"Ollama request timed out after {self.timeout}s"
                ) from e

            except requests.exceptions.HTTPError as e:
                logger.error(f"Ollama HTTP error: {e}")
                raise OllamaError(f"Ollama request failed: {e}") from e

            except Exception as e:
                logger.error(f"Ollama request failed: {e}")
                raise OllamaError(f"Ollama request failed: {e}") from e

        raise OllamaError("Max retries exceeded")

    def check_health(self) -> bool:
        """
        Check if Ollama server is healthy and model is available.

        Returns:
            True if healthy and model available, False otherwise
        """
        try:
            # Check server health
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()

            # Check if model is available
            tags_data = response.json()
            models = [m["name"] for m in tags_data.get("models", [])]

            # Check for exact match or base model match (e.g., "llama3.2:latest" matches "llama3.2")
            model_base = self.model.split(":")[0]
            model_found = any(
                self.model == m or m.startswith(model_base) for m in models
            )

            if not model_found:
                logger.warning(f"Model '{self.model}' not found. Available: {models}")
                return False

            logger.debug(f"Ollama health check passed (model: {self.model})")
            return True

        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.host}")
            return False
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    def list_models(self) -> list[str]:
        """
        List available models.

        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            tags_data = response.json()
            return [m["name"] for m in tags_data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
