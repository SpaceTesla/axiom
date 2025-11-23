import asyncio
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config import Settings


class LLMService:
    """Service for handling LLM interactions."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.google_api_key
        )
        self._system_prompt = None
    
    @property
    def system_prompt(self) -> str:
        """Load and cache system prompt from file."""
        if self._system_prompt is None:
            prompt_path = Path(self.settings.prompt_file_path)
            if not prompt_path.exists():
                raise FileNotFoundError(
                    f"Prompt file not found: {prompt_path}"
                )
            self._system_prompt = prompt_path.read_text(encoding="utf-8")
        return self._system_prompt
    
    def _generate_sync(self, user_message: str) -> str:
        """Synchronous LLM generation."""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message),
        ]
        response = self.llm.invoke(messages)
        
        # Handle Gemini response format - content can be a list or string
        if isinstance(response.content, list):
            # Extract text from content blocks
            text_parts = []
            for block in response.content:
                if isinstance(block, dict) and "text" in block:
                    text_parts.append(block["text"])
                elif isinstance(block, str):
                    text_parts.append(block)
            return "".join(text_parts) if text_parts else str(response.content)
        
        return str(response.content)
    
    async def generate_response(self, user_message: str) -> str:
        """Generate LLM response for the given user message."""
        return await asyncio.to_thread(self._generate_sync, user_message)

