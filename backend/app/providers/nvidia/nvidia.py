from typing import AsyncGenerator, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from app.core.config.settings import settings
from app.core.exceptions.handler import LLMProviderException
from app.core.logger.logging import logger
from app.providers.base.provider import BaseLLMProvider


class NvidiaLlamaProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        key = api_key or settings.LLM_API_KEY
        selected_model = model or settings.LLM_MODEL or "stepfun-ai/step-3.7-flash"
        self.client = ChatNVIDIA(
            model=selected_model,
            api_key=key,
            temperature=1,
            top_p=0.95,
            max_completion_tokens=settings.LLM_MAX_COMPLETION_TOKENS,
        )

    def _build_messages(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> list[SystemMessage | HumanMessage]:
        messages: list[SystemMessage | HumanMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        return messages

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        try:
            response = await self.client.ainvoke(self._build_messages(prompt, system_prompt))
            content = response.content
            if isinstance(content, list):
                return "".join(str(part) for part in content)
            return str(content)
        except Exception as exc:
            logger.exception("NVIDIA LLM generation failed")
            raise LLMProviderException(f"NVIDIA LLM generation failed: {str(exc)}")

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        try:
            async for chunk in self.client.astream(self._build_messages(prompt, system_prompt)):
                content = chunk.content
                if isinstance(content, list):
                    text = "".join(str(part) for part in content)
                else:
                    text = str(content)
                if text:
                    yield text
        except Exception as exc:
            logger.exception("NVIDIA LLM streaming failed")
            raise LLMProviderException(f"NVIDIA LLM streaming failed: {str(exc)}")
