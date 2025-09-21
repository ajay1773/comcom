from app.models.chat import GlobalState
from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.core.enums import TypeIntentType
from app.services.chat_history_state import get_conversation_context_for_workflow
import re

class IntentClassification(BaseModel):
    """Classifier must return one of the defined intents."""
    intent: TypeIntentType
    confidence: float
    disfluent_message: str

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PASSWORD_REGEX = r"password\s*[:=]?\s*\S+"

# --- Add a static fallback map ---
DISFLUENCY_MAP = {
    "product_search": "Searching for the product you need...",
    "place_order": "Processing your order request...",
    "initiate_payment": "Processing your payment request...",
    "payment_status": "Processing your payment request...",
    "support_query": "Looking into support options for you...",
    "faq": "Finding an answer for you...",
    "smalltalk": "Let's have a quick chat...",
    "unknown": "Trying to understand your request...",
    "generate_signin_form": "Processing your signin request...",
    "login_with_credentials": "Processing your login request...",
    "generate_signup_form": "Processing your signup request...",
    "signup_with_details": "Creating your account..."
}

parser = PydanticOutputParser(pydantic_object=IntentClassification)


def enforce_login_rules(intent: str, user_message: str) -> str:
    has_email = re.search(EMAIL_REGEX, user_message) is not None
    has_password = re.search(PASSWORD_REGEX, user_message, re.IGNORECASE) is not None

    if intent == "login_with_credentials" and not (has_email and has_password):
        return "generate_signin_form"
    return intent




async def classifier_node(state: GlobalState) -> GlobalState:
    """
    LangGraph node for classifying the user query with conversation history context.
    """
    user_message = state.get("user_message", "")
    if not user_message:
        return state

    # Get conversation context for better intent classification
    conversation_context = get_conversation_context_for_workflow(state, limit=5)

    # Build context-aware prompt
    context_section = ""
    if conversation_context:
        context_section = f"""
        CONVERSATION CONTEXT:
        The following is the recent conversation history to help you better understand the user's intent and context:

        {conversation_context}

        Use this context to:
        - Understand if this is a continuation of a previous conversation
        - Identify references to previously mentioned products or workflows
        - Better classify the user's current intent based on conversation flow
        - Detect if the user is referring back to previous interactions
        """

    # Create dynamic prompt with conversation context
    dynamic_classifier_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
        You are an intent classifier and disfluency message generator.

        Your task:
        1. Classify a given user message into one of the following intents.
        Each intent has strong, mutually exclusive rules.
        Always select the single BEST-FIT workflow purely based on the user's intent.

        - add_to_cart: For adding a product to the cart. Use when:
          * User explicitly says "add to cart", "add to my cart", "put in my cart", "add item"
          PRIORITY RULE: This intent OVERRIDES product_search, place_order, or any other intent
          whenever such phrases are present in the user message.

        - product_search: ONLY for when the user is **browsing, discovering, or asking about product availability/categories**.
        Examples:
          * "Show me blue sweaters for men"
          * "Find blue shirts"
          * "Do you have any Nike shoes?"
          * "Search for winter jackets"

        - place_order: For purchasing/ordering SPECIFIC products. Use when:
          * User explicitly mentions ordering/buying a specific product
          * User uses phrases like "order", "buy", "purchase" with a product name
          * User wants to proceed with purchasing a known product
          Examples:
          * "I'd like to order the Blue Comfort T-shirt by Nike"
          * "I want to buy the Leather Jacket by Fashion Corp"
          * "Let me purchase the Red Sneakers"
          * "Place order for Summer Breeze Dress"

        - initiate_payment: For generating a payment link. Use when:
          * User wants to initiate payment for a specific product
          * User uses phrases like "pay", "pay for", "make payment" with a product name
          * User wants to proceed with purchasing a known product
          Examples:
          * "I want to pay for the Blue Comfort T-shirt by Nike"
          * "Make payment for the Leather Jacket by Fashion Corp"
          * "Let me pay for the Red Sneakers"
          * "Initiate payment for Summer Breeze Dress"

        - payment_status: For making a payment with credit card details. Use when:
          * User wants to make a payment with credit card details
          * User uses phrases like "make payment with credit card", "check payment", "payment status"
          Examples:
          * "Make payment with credit card for the Blue Comfort T-shirt by Nike"
          * "Make payment with credit card for the Leather Jacket by Fashion Corp"
          * "Let me make payment with credit card for the Red Sneakers"
          * "Make payment with credit card for Summer Breeze Dress"

        - generate_signin_form: For showing the login/sign-up form to the user.
          Use when:
            * The user wants to sign in or sign up but has NOT provided BOTH an email AND a password in the same message.
            * This includes cases where:
                - They provide neither ("I want to login")
                - They provide only email ("My email is test@example.com")
                - They provide only password ("My password is 123456")
            * DO NOT use this if both email and password are present together.
          Examples:
            * "I want to sign in"
            * "Sign up for an account"
            * "Here is my email: ajay@example.com"
            * "My password is hunter2"
            * "Let me login"

        - login_with_credentials: When user sends BOTH email and password together in the SAME message.
          Use when:
            * The user explicitly provides BOTH fields: email AND password.
            * Do NOT use this if only one field is present.
          Examples:
            * "Here are my login credentials: email ajay@example.com and password 123456"
            * "Login with email: foo@bar.com and password: secret123"
            * "I would like to login with following credentials: email=hello@test.com password=pass123"

        - generate_signup_form: For sending a signup form to the user. Use when:
          * User wants to sign up
          * User uses phrases like "sign up", "sign up for an account", "register for an account"
          * Always execute before signup_with_details
          * Always must include email and password in the prompt
          Examples:
          * "I want to sign up"
          * "Sign up for an account"
          * "Let me register"
          * "Sign up for an account"

        - signup_with_details: For signing up with details. Use when:
          * User wants to sign up with details
          * User uses phrases like "sign up with details", "register with details"
          * Always execute before save_user_details
          * Always must include email and password in the prompt
          Examples:
          * "I want to sign up with email <email> and password <password> and first name <first_name> and last name <last_name> and phone <phone>"
          * "Let me sign up with email <email> and password <password> and first name <first_name> and last name <last_name> and phone <phone>"

        - support_query: For customer support related queries
        - faq: For general questions about the service
        - smalltalk: For casual conversation, general questions about capabilities
        - unknown: When the intent is unclear

        IMPORTANT DISTINCTION:
        - If user is discovering/searching → product_search
        - If user wants to buy a specific product → place_order
        - If user wants to initiate payment for a specific product → initiate_payment
        - If user wants to make a payment with credit card details → payment_status
        - If user explicitly says "add to cart" or any variation (e.g. "add this", "put in my cart", "add item to cart") → ALWAYS choose add_to_cart
        - Even if the product is mentioned, if the action is "add to cart", do not classify as product_search.


        CRITICAL RULES FOR LOGIN INTENTS:
        1. login_with_credentials:
          - Trigger ONLY if the user message contains BOTH:
              (a) a valid email address (something containing "@" and a domain),
              AND
              (b) a password (any non-empty text following the word "password").
          - If BOTH are present in the SAME message → ALWAYS choose login_with_credentials.
          - Example:
              "Here are my login credentials: Email = user@example.com, Password = secret123"

        2. generate_signin_form:
          - Trigger if:
              (a) The user wants to log in / sign in, BUT
              (b) They have NOT provided BOTH email AND password in the same message.
          - This includes:
              - No email or password
              - Only email
              - Only password
          - Example:
              "I want to sign in"
              "My email is test@example.com"
              "My password is 123456"

        IMPORTANT:
        - If both email AND password appear → DO NOT use generate_signin_form. Use login_with_credentials instead.
        - If only one or none appear → DO NOT use login_with_credentials. Use generate_signin_form instead.


        2. Generate a "disfluent message":
        - This is a short, natural, conversational message shown to the user while the system processes their request.
        - The message should match the intent and sound fluent, polite, and helpful.
        - Examples:
            - If intent = product_search → "Searching for the product you need..."
            - If intent = place_order → "Processing your order request..."
            - If intent = initiate_payment → "Processing your payment request..."
            - If intent = payment_status → "Processing your payment request..."
            - If intent = support_query → "Looking into support options for you..."
            - If intent = generate_signup_form → "Processing your signup request..."
            - If intent = payment_status → "Processing your payment request..."
            - If intent = faq → "Finding an answer for you..."
            - If intent = smalltalk → "Let's have a quick chat..."
            - If intent = unknown → "Trying to understand your request..."
            - If intent = generate_signin_form → "Processing your signin request..."
            - If intent = login_with_credentials → "Processing your login request..."
            - If intent = generate_signup_form → "Processing your signup request..."
            - If intent = signup_with_details → "Creating your account..."
            - If intent = add_to_cart → "Adding your product to cart..."
        3. Provide a confidence score between 0.0 and 1.0 indicating how certain you are about the intent classification.

        Output format:
        Return **only valid JSON** with the following fields:
        - `intent`: one of [product_search, place_order, initiate_payment, payment_status, support_query, faq, smalltalk, unknown, generate_signin_form, login_with_credentials, generate_signup_form, signup_with_details]
        - `confidence`: float between 0.0 and 1.0
        - `disfluent_message`: string

        Do not include any explanations or text outside of JSON.
        """ + context_section),
        ("user", "{user_message}")
    ])

    llm_response = await llm_service.get_llm_without_tools(disable_streaming=True).with_structured_output(IntentClassification).ainvoke(dynamic_classifier_prompt.invoke({"user_message": user_message}))

    # Cast to IntentClassification for type safety
    response: IntentClassification = llm_response  # type: ignore

    # Apply enforcement
    corrected_intent = enforce_login_rules(response.intent, user_message)

    # If enforcement changed intent, correct disfluency
    if corrected_intent != response.intent:
        disfluent_message = DISFLUENCY_MAP.get(corrected_intent, "Processing your request...")
    else:
        disfluent_message = response.disfluent_message or DISFLUENCY_MAP.get(corrected_intent, "Processing your request...")

    # Update state with new values
    state["intent"] = corrected_intent
    state["confidence"] = response.confidence
    state["disfluent_message"] = disfluent_message

    return state
