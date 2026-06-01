from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        json_mode: bool = False
    ) -> str:
        """
        Generates text using the provider.
        """
        pass

    @abstractmethod
    async def generate_stream(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generates text as an async stream.
        """
        pass
