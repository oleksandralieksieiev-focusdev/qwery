from langchain.llms.base import LLM
from pydantic import BaseModel
from constants import OLLAMA_MODEL, OLLAMA_URL
import requests


class OllamaLLM(LLM, BaseModel):
    model: str = OLLAMA_MODEL
    url: str = OLLAMA_URL
    temperature: float = 0.0
    max_tokens: int = 16000

    class Config:
        arbitrary_types_allowed = True

    def _call(self, prompt: str, **kwargs) -> str:
        # send prompt to Ollama HTTP generate endpoint
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        try:
            resp = requests.post(self.url, json=payload, timeout=3600)
            resp.raise_for_status()
            data = resp.json()
            # adjust depending on Ollama response shape; common key "response" or "text"
            if isinstance(data, dict):
                if "response" in data:
                    return data["response"]
                if "text" in data:
                    return data["text"]
            # fallback: raw text
            return resp.text
        except Exception as e:
            raise RuntimeError(f"Ollama request failed: {e}")

    @property
    def _identifying_params(self):
        return {"model": self.model}

    @property
    def _llm_type(self):
        return "ollama"
