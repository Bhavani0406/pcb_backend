from app.providers.base.openai_compatible import BaseOpenAICompatibleProvider
from app.core.config.settings import settings

class GroqLlamaProvider(BaseOpenAICompatibleProvider):
    def __init__(self, api_key: str = None, model: str = None):
        api_url = settings.LLM_API_URL or "https://api.groq.com/openai/v1/chat/completions"
        key = api_key or settings.LLM_API_KEY
        selected_model = model or settings.LLM_MODEL or "llama-3.3-70b-versatile"
        super().__init__(api_url=api_url, api_key=key, model=selected_model)
