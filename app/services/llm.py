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
        # Include more messages for better context, but limit to avoid token limits
        context = "\n".join(conversation_history[:8])  # First 8 messages for better context
        
        prompt = f"""You are an AI assistant that creates concise, descriptive titles for conversations. Based on the conversation below, generate a short title (2-5 words) that captures the main topic, intent, or purpose.

Even if the conversation is very short (just 1-2 messages), focus on the user's intent or what they're asking about.

Conversation:
{context}

Guidelines:
- Focus on the user's main intent or the primary topic discussed
- Use specific terms when possible (e.g., "iPhone Search" instead of "Product Search")
- For short conversations, extract the key topic from the user's first message
- Avoid generic words like "help", "chat", "conversation" unless necessary
- Make it actionable or descriptive of the content
- Keep it under 50 characters

Examples of good titles:
- "iPhone 15 Search" (from "I'm looking for iPhone 15")
- "Order Status Check" (from "What's my order status?")
- "Password Reset" (from "I forgot my password")
- "Shipping Address Update" (from "Need to change my address")
- "Product Recommendations" (from "Can you recommend products?")
- "Account Billing Issue" (from "Problem with my bill")
- "Return Policy Question" (from "What's your return policy?")

Generate only the title, no quotes or extra text:"""

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
            
            # Remove any trailing punctuation
            title = title.rstrip('.,!?:;')
            
            # Ensure title is not too long
            if len(title) > 50:
                title = title[:47] + "..."
            
            # Capitalize first letter of each word for consistency
            title = title.title()
            
            return title if title else "New Chat"
            
        except Exception as e:
            print(f"Failed to generate conversation title: {e}")
            return "New Chat"


llm_service = LLMService()
