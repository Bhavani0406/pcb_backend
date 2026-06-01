from app.providers.base.openai_compatible import BaseOpenAICompatibleProvider
from app.core.config.settings import settings

class OllamaLlamaProvider(BaseOpenAICompatibleProvider):
    def __init__(self, api_key: str = None, model: str = None):
        api_url = settings.LLM_API_URL or "http://localhost:11434/v1/chat/completions"
        key = api_key or settings.LLM_API_KEY or "ollama"  # Ollama usually ignores api key
        selected_model = model or settings.LLM_MODEL or "llama3"
        super().__init__(api_url=api_url, api_key=key, model=selected_model)
