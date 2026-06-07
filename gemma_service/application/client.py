from abc import ABC, abstractmethod
import json
from urllib import error, request


class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: str) -> str:
        raise NotImplementedError


class DummyLLMClient(LLMClient):
    def generate(self, prompt: str, model: str) -> str:
        return f"[{model}] {prompt[:120]}"


class OllamaClient(LLMClient):  # pragma: no cover - optional networked integration
    def __init__(self, base_url: str, timeout_seconds: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate(self, prompt: str, model: str) -> str:
        payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except error.URLError as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc
        return body
