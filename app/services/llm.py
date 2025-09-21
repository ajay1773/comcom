# app/services/llm.py

from langchain_ollama import ChatOllama
from app.core.config import settings
from langchain_groq import ChatGroq
from pydantic import SecretStr

class LLMService:
    def __init__(self):
        self.ollama_model = settings.OLLAMA_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.groq_model = settings.GROQ_MODEL
        self.groq_api_key = settings.GROQ_API_KEY
        self.groq_model_instance = ChatGroq(
            model=self.groq_model,
            api_key= SecretStr(self.groq_api_key),
            temperature=self.temperature,
        )
        self.ollama_model_instance = ChatOllama(
            model=self.ollama_model,
            temperature=self.temperature,
        )
    

    def get_llm(self, disable_streaming: bool = False) -> ChatGroq:
        """
        Return a ChatGroq instance.
        Note: disable_streaming parameter kept for compatibility but handled at stream level.
        """
        return self.groq_model_instance

    def get_llm_without_tools(self, disable_streaming: bool = False) -> ChatGroq:
        """Alias for getting a model, usually used for structured output or extractors."""
        return self.get_llm(disable_streaming=disable_streaming)



llm_service = LLMService()
