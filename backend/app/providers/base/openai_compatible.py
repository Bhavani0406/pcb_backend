import json
import httpx
from typing import AsyncGenerator, Optional, Dict, Any
from app.providers.base.provider import BaseLLMProvider
from app.core.exceptions.handler import LLMProviderException
from app.core.logger.logging import logger

class BaseOpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self, api_url: str, api_key: str, model: str):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        json_mode: bool = False
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self._get_headers(),
                    json=payload
                )
                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"LLM API Error {response.status_code}: {error_detail}")
                    raise LLMProviderException(f"LLM Provider API returned status {response.status_code}: {error_detail}")
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            logger.error(f"HTTP request error during LLM generation: {str(e)}")
            raise LLMProviderException(f"Network error communicating with LLM Provider: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error in LLM generation")
            raise LLMProviderException(f"LLM Generation failed: {str(e)}")

    async def generate_stream(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "stream": True
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    self.api_url,
                    headers=self._get_headers(),
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        error_detail = await response.aread()
                        logger.error(f"LLM Stream API Error {response.status_code}: {error_detail.decode()}")
                        raise LLMProviderException(f"LLM Provider Stream API returned status {response.status_code}")

                    async for line in response.iter_lines():
                        if not line:
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data_json = json.loads(data_str)
                                delta = data_json["choices"][0]["delta"]
                                if "content" in delta:
                                    yield delta["content"]
                            except Exception:
                                continue
        except httpx.HTTPError as e:
            logger.error(f"HTTP stream error during LLM generation: {str(e)}")
            raise LLMProviderException(f"Network error in LLM Stream: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error in LLM streaming")
            raise LLMProviderException(f"LLM Streaming failed: {str(e)}")
