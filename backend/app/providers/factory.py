from app.providers.base.provider import BaseLLMProvider
from app.providers.groq.groq import GroqLlamaProvider
from app.providers.ollama.ollama import OllamaLlamaProvider
from app.providers.openrouter.openrouter import OpenRouterLlamaProvider
from app.providers.together.together import TogetherAILlamaProvider, OpenAICompatibleLlamaProvider
from app.providers.nvidia.nvidia import NvidiaLlamaProvider
from app.core.config.settings import settings
from app.core.exceptions.handler import LLMProviderException
from app.core.logger.logging import logger

class LLMProviderFactory:
    @staticmethod
    def get_provider(provider_name: str = None) -> BaseLLMProvider:
        name = (provider_name or settings.LLM_PROVIDER or "groq").lower().strip()
        logger.info(f"Instantiating LLM Provider: {name}")

        if name == "groq":
            return GroqLlamaProvider()
        elif name == "ollama":
            return OllamaLlamaProvider()
        elif name == "openrouter":
            return OpenRouterLlamaProvider()
        elif name == "together":
            return TogetherAILlamaProvider()
        elif name == "openai":
            return OpenAICompatibleLlamaProvider()
        elif name == "nvidia":
            return NvidiaLlamaProvider()
        else:
            logger.warning(f"Unknown LLM Provider '{name}'. Falling back to Groq.")
            return GroqLlamaProvider()
