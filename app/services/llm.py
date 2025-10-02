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

    async def generate_conversation_title(self, conversation_history: list[str]) -> str:
        """Generate a concise title for a conversation based on its history."""
        if not conversation_history:
            return "New Chat"
        
        # Take the first few messages to understand the conversation topic
        context = "\n".join(conversation_history[:6])  # First 6 messages
        
        prompt = f"""Based on the following conversation, generate a short, descriptive title (maximum 4-5 words) that captures the main topic or purpose of the conversation. The title should be clear and concise.

Conversation:
{context}

Generate only the title, nothing else. Examples of good titles:
- "Product Search Help"
- "Order Status Inquiry" 
- "Account Setup"
- "Payment Issue"
- "Shopping Cart"

Title:"""

        try:
            llm = self.get_llm(disable_streaming=True)
            response = await llm.ainvoke(prompt)
            
            # Extract and clean the title
            title = response.content.strip()
            
            # Remove quotes if present
            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]
            if title.startswith("'") and title.endswith("'"):
                title = title[1:-1]
            
            # Ensure title is not too long
            if len(title) > 50:
                title = title[:47] + "..."
            
            return title if title else "New Chat"
            
        except Exception as e:
            print(f"Failed to generate conversation title: {e}")
            return "New Chat"


llm_service = LLMService()
