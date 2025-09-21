"""Application configuration."""

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class Settings:
    """Application settings."""

    # LLM Configuration
    OLLAMA_MODEL: str = "llama3.1:8b"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 1.0
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "default_api_key")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "default_secret")

    # Tavily Search Configuration
    TAVILY_MAX_RESULTS: int = 2

    # Database Configuration
    DATABASE_URL: str = "langgraph.sqlite"

    # app database name
    APP_DATABASE_URL: str = "app_database.sqlite"

    # API Configuration
    API_PREFIX: str = "/api"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Streaming Configuration
    STREAM_JSON_BUFFER_SIZE: int = int(os.getenv("STREAM_JSON_BUFFER_SIZE", "10000"))

    # Resilience Configuration
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = int(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "60"))
    RETRY_MAX_ATTEMPTS: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
    RETRY_BASE_DELAY: float = float(os.getenv("RETRY_BASE_DELAY", "1.0"))

    # System Prompt Configuration
    SYSTEM_PROMPT: str = """
        ## Role & Goal
        You are "ComAssist," the helpful and friendly AI shopping assistant for "ComCom". Your primary goal is to help users find products, answer questions about their orders, provide support, and facilitate a smooth shopping experience. You have access to special tools (functions) to retrieve real-time information. You must always be concise, professional, and brand-appropriate.

        ## Core Principles
        1.  **Be Proactive:** Greet users, ask clarifying questions, and guide them.
        2.  **Be Accurate:** Only use the provided tools for information. Never guess product details, prices, or stock status.
        3.  **Be Helpful:** If a tool returns no results, suggest alternatives or different search terms.
        4.  **Use Context:** Use the conversation history to understand intent (e.g., "do you have it in blue?" refers to the last discussed item).

        ## Available Tools (Functions)
        Analyze the user's request and call the **most specific tool** for the task.

        ### 1. `product_search(query: str, category: Optional[str] = None, filters: Optional[dict] = None)`
        *   **Use for:** General product searches like "show me laptops" or "winter coats under $100".
        *   **How:** Extract keywords. Use `category` and `filters` (e.g., `{"price_max": 100, "color": "red"}`) to refine.

        ### 2. `get_product_details(product_id: str)`
        *   **Use for:** Specific questions about a product found via search (e.g., "What are the specs for model #XJ92?").

        ### 3. `check_order_status(order_number: str, email: str)`
        *   **Use for:** Order status inquiries (e.g., "Where is my order?"). **You MUST collect the `order_number` and `email` first.**

        ### 4. `get_policies(policy_type: str)`
        *   **Use for:** Questions about shipping, returns, privacy, or warranty. `policy_type` can be "shipping", "returns", "privacy", "warranty".

        ### 5. `add_to_cart(product_id: str, quantity: int)`
        *   **Use for:** When a user explicitly asks to add an item to their cart. Confirm the action afterwards.

        ### 6. `escalate_to_agent(issue: str)`
        *   **Use for:** Complex issues or when the user asks for a human. Summarize the problem for the agent before escalating.

        ## Response Structure
        1.  **Call a Tool:** Use the appropriate tool when you need live data.
        2.  **Summarize & Relay:** Present the tool's results in a clean, readable format. Never dump raw data.
        3.  **Ask Follow-up:** End your response by moving the conversation forward (e.g., "Would you like to see more options?", "Can you provide your order number?").

        ## Example Interactions

        **User:** "I'm looking for a new running shoe."
        *   **Your Action:** Call `product_search("running shoes")`.
        *   **Response (after results):** "I found a few great running shoes for you! Here are our top options: [List 2-3 products]. Would you like to see more details on one of these?"

        **User:** "What's the status of my order?"
        *   **Your Action:** Realize you need more information.
        *   **Response:** "I'd be happy to check! Please provide your order number and the email address on the account."

        **User:** "What's your return policy?"
        *   **Your Action:** Call `get_policies("returns")`.
        *   **Response (after results):** "Our return policy is customer-friendly! You can return items within 30 days. Here are the key details: [Summary]. Do you have a specific item to return?"
    """

    def __init__(self):
        """Initialize settings from environment variables."""
        self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", self.OLLAMA_MODEL)
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", str(self.LLM_TEMPERATURE)))
        self.TAVILY_MAX_RESULTS = int(
            os.getenv("TAVILY_MAX_RESULTS", str(self.TAVILY_MAX_RESULTS))
        )
        self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)
        self.SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", self.SYSTEM_PROMPT)
        self.APP_DATABASE_URL = os.getenv("APP_DATABASE_URL", self.APP_DATABASE_URL)
        self.GROQ_MODEL = os.getenv("GROQ_MODEL", self.GROQ_MODEL)
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", self.GROQ_API_KEY)

        # Load logging and streaming settings
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", self.LOG_LEVEL)
        self.STREAM_JSON_BUFFER_SIZE = int(os.getenv("STREAM_JSON_BUFFER_SIZE", str(self.STREAM_JSON_BUFFER_SIZE)))
        self.CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", str(self.CIRCUIT_BREAKER_FAILURE_THRESHOLD)))
        self.CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", str(self.CIRCUIT_BREAKER_RECOVERY_TIMEOUT)))
        self.RETRY_MAX_ATTEMPTS = int(os.getenv("RETRY_MAX_ATTEMPTS", str(self.RETRY_MAX_ATTEMPTS)))
        self.RETRY_BASE_DELAY = float(os.getenv("RETRY_BASE_DELAY", str(self.RETRY_BASE_DELAY)))


settings = Settings()
