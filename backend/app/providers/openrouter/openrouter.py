from app.providers.base.openai_compatible import BaseOpenAICompatibleProvider
from app.core.config.settings import settings
from typing import Dict

class OpenRouterLlamaProvider(BaseOpenAICompatibleProvider):
    def __init__(self, api_key: str = None, model: str = None):
        api_url = settings.LLM_API_URL or "https://openrouter.ai/api/v1/chat/completions"
        key = api_key or settings.LLM_API_KEY
        selected_model = model or settings.LLM_MODEL or "meta-llama/llama-3.3-70b-instruct"
        super().__init__(api_url=api_url, api_key=key, model=selected_model)

    def _get_headers(self) -> Dict[str, str]:
        headers = super()._get_headers()
        # OpenRouter suggests these headers for identification
        headers["HTTP-Referer"] = "https://github.com/google/antigravity"
        headers["X-Title"] = "PCB AI Interview Platform"
        return headers
