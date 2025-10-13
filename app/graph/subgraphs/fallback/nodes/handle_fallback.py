from app.models.chat import GlobalState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.utils.conversation_context import format_conversation_context_with_template
import re

async def handle_fallback_node(state: GlobalState) -> GlobalState:
    """
    Enhanced fallback handler for comprehensive conversation management.
    Handles smalltalk, FAQ, support queries, capabilities questions, and out-of-scope requests.
    """
    user_message = state.get("user_message", "")
    intent = state.get("intent", "unknown")

    # Determine conversation type and generate appropriate response
    conversation_type = _classify_conversation_type(user_message, intent or "unknown")
    response_text = await _generate_contextual_response(user_message, conversation_type, state)

    # Update state with response
    state["workflow_output_text"] = response_text
    state["workflow_output_json"] = {
        "template": "fallback_response",
        "payload": {
            "intent": intent,
            "conversation_type": conversation_type,
            "response_type": "conversational",
            "user_query": user_message,
            "ecommerce_focused": True
        }
    }

    return state

def _classify_conversation_type(user_message: str, intent: str) -> str:
    """
    Classify the type of conversation for more targeted responses.
    """
    message_lower = user_message.lower()
    
    # Greeting patterns
    greeting_patterns = [
        r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
        r'\bhow are you\b',
        r'\bwhat\'s up\b'
    ]
    
    # Capabilities/help patterns
    capability_patterns = [
        r'\bwhat can you (do|help)\b',
        r'\bwhat are your (capabilities|features)\b',
        r'\bhow can you help\b',
        r'\bwhat services do you (offer|provide)\b',
        r'\bwhat do you do\b',
        r'\bhelp me\b'
    ]
    
    # Farewell patterns
    farewell_patterns = [
        r'\b(bye|goodbye|see you|thanks|thank you)\b',
        r'\bthat\'s all\b',
        r'\bi\'m done\b'
    ]
    
    # Out of scope patterns (non-ecommerce)
    out_of_scope_patterns = [
        r'\b(weather|news|politics|sports|movies|music)\b',
        r'\b(recipe|cooking|travel|health|medical)\b',
        r'\b(programming|code|software|tech support)\b',
        r'\bwhat time is it\b',
        r'\btell me a joke\b'
    ]
    
    # Check patterns
    if any(re.search(pattern, message_lower) for pattern in greeting_patterns):
        return "greeting"
    elif any(re.search(pattern, message_lower) for pattern in capability_patterns):
        return "capabilities"
    elif any(re.search(pattern, message_lower) for pattern in farewell_patterns):
        return "farewell"
    elif any(re.search(pattern, message_lower) for pattern in out_of_scope_patterns):
        return "out_of_scope"
    elif intent == "smalltalk":
        return "smalltalk"
    elif intent == "faq":
        return "faq"
    elif intent == "support_query":
        return "support_query"
    else:
        return "unknown"

async def _generate_contextual_response(user_message: str, conversation_type: str, state: GlobalState = None) -> str:
    """
    Generate contextual responses based on conversation type.
    """
    try:
        if conversation_type == "greeting":
            return await _handle_greeting(user_message, state)
        elif conversation_type == "capabilities":
            return await _handle_capabilities_inquiry(user_message, state)
        elif conversation_type == "farewell":
            return await _handle_farewell(user_message, state)
        elif conversation_type == "out_of_scope":
            return await _handle_out_of_scope(user_message, state)
        elif conversation_type == "smalltalk":
            return await _handle_smalltalk(user_message, state)
        elif conversation_type == "faq":
            return await _handle_faq(user_message, state)
        elif conversation_type == "support_query":
            return await _handle_support_query(user_message, state)
        else:  # unknown
            return await _handle_unknown(user_message, state)
    except Exception:
        # Fallback to safe default response
        return await _get_default_ecommerce_response(user_message, state)

async def _handle_greeting(user_message: str, state: GlobalState = None) -> str:
    """Handle greetings with ecommerce context."""
    try:
        # Get conversation context
        conversation_context = format_conversation_context_with_template(
            state=dict(state) if state else {},
            template_name="general",
            limit=5,
            fallback_message=""
        ) if state else ""
        
        greeting_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                # System Prompt - Role Section for E-commerce Chatbot

                ## Your Role

                You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter. You represent the voice of COMCOM in every interaction.

                ## Core Identity

                - You are helpful, enthusiastic, and genuinely invested in creating an excellent shopping experience
                - You combine the expertise of a product specialist with the warmth of a trusted friend
                - You communicate in a conversational tone that feels natural and approachable
                - You are patient, never rushed, and always prioritize the customer's needs over making a quick sale

                ## Your Communication Style

                **Tone & Approach:**
                - Be warm and welcoming, but respect the customer's time by being efficient
                - Use conversational language that feels human, not robotic or scripted
                - Show enthusiasm for products without being pushy or overly salesy
                - Use "I" and "you" to create a personal connection

                Respond to greetings warmly and naturally. Always include a brief mention of how you can help with shopping.
                Keep responses concise (1-2 sentences) and welcoming.
                """),
            ("user", "{message}"),
            ("user", "{conversation_context}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(greeting_prompt.invoke({"message": user_message, "conversation_context": conversation_context}))
        return str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
    except Exception:
        return "Hello! I'm your ecommerce assistant. I can help you search for products, manage your cart, place orders, and handle your account. What would you like to do today?"

async def _handle_capabilities_inquiry(user_message: str, state: GlobalState = None) -> str:
    """Handle questions about what the assistant can do."""
    try:
        # Get conversation context
        conversation_context = format_conversation_context_with_template(
            state=dict(state) if state else {},
            template_name="general",
            limit=5,
            fallback_message=""
        ) if state else ""
        
        capabilities_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                ## Your Role

                You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter. You represent the voice of COMCOM in every interaction.

                ## Your Capabilities

                You can assist customers with:
                - Product discovery
                - Processing orders
                - Tracking shipments and providing delivery updates
                - Handling returns, exchanges, and refunds
                - Troubleshooting issues with orders or accounts
                - Explaining company policies (shipping, returns, warranties, etc.)

                ## Your Communication Style

                **Tone & Approach:**
                - Be warm and welcoming, but respect the customer's time by being efficient
                - Use conversational language that feels human, not robotic or scripted
                - Show enthusiasm for products without being pushy or overly salesy
                - Use "I" and "you" to create a personal connection

                **Proactive Assistance:**
                - Anticipate needs based on the conversation context
                - Offer relevant suggestions without being intrusive
                - Provide complete information upfront to minimize back-and-forth
                - Suggest next steps to keep the customer's journey moving forward

                Provide a comprehensive but friendly overview of what you can help with.
                Tailor your response to their specific question while covering these key areas.
                Be conversational and include examples of how they can interact with you.
                Always reply in markdown.
                """),
            ("user", "{message}"),
            ("user", "{conversation_context}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(capabilities_prompt.invoke({"message": user_message, "conversation_context": conversation_context}))
        return str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
    except Exception:
        return """**Welcome to your personal style consultation!** Here's how I can elevate your fashion journey:

🎨 **Style Consultation & Product Discovery:**
• Curate products based on your personal style preferences
• Provide expert advice on fit, fabric, and styling
• Search our collection by style, occasion, or specific pieces
• Suggest complementary items and complete looks

🛍️ **Personal Shopping Experience:**
• Build and manage your curated cart
• Guide you through size selection and fit considerations
• Process orders with attention to your style preferences

👤 **Style Profile Management:**
• Create and maintain your style profile
• Save preferred sizes, colors, and style preferences
• Manage delivery addresses for seamless shopping

📦 **Order & Style Journey Tracking:**
• Monitor your fashion purchases and style evolution
• Provide styling tips for your purchased pieces
• Secure payment processing with style-focused service

💬 **Fashion Expertise & Support:**
• Answer questions about fabrics, care, and styling
• Provide trend insights and seasonal recommendations
• Help you build a cohesive wardrobe

**Let's start your style journey!** Try saying *"find me a sophisticated blazer"* or *"show me my style profile"*."""

async def _handle_farewell(user_message: str, state: GlobalState = None) -> str:
    """Handle goodbye messages."""
    try:
        # Get conversation context
        conversation_context = format_conversation_context_with_template(
            state=dict(state) if state else {},
            template_name="general",
            limit=5,
            fallback_message=""
        ) if state else ""
        
        farewell_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                ## Your Role

                You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter.

                ## Your Communication Style

                **Tone & Approach:**
                - Be warm and welcoming, but respect the customer's time by being efficient
                - Use conversational language that feels human, not robotic or scripted
                - Use "I" and "you" to create a personal connection

                **Empathy & Understanding:**
                - Celebrate positive moments ("Congratulations on your purchase! You made a great choice!")
                - Show genuine care when customers face issues

                Say goodbye to a customer warmly and professionally.
                Invite them to return for future shopping needs.
                Keep it brief and friendly.
                Always reply in markdown.
                """),
            ("user", "{message}"),
            ("user", "{conversation_context}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(farewell_prompt.invoke({"message": user_message, "conversation_context": conversation_context}))
        return str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
    except Exception:
        return "Thank you for shopping with us! Feel free to come back anytime for your shopping needs. Have a great day!"

async def _handle_out_of_scope(user_message: str, state: GlobalState = None) -> str:
    """Handle requests outside of ecommerce scope."""
    try:
        # Get conversation context
        conversation_context = format_conversation_context_with_template(
            state=dict(state) if state else {},
            template_name="general",
            limit=5,
            fallback_message=""
        ) if state else ""
        
        out_of_scope_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                ## Your Role

                You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter.

                ## Your Communication Style

                **Tone & Approach:**
                - Be warm and welcoming, but respect the customer's time by being efficient
                - Use conversational language that feels human, not robotic or scripted
                - Use "I" and "you" to create a personal connection

                ## Boundaries & Limitations

                - You cannot make subjective judgments about which product is "best"—instead, help customers understand options based on their specific needs
                - You focus on ecommerce and shopping-related assistance

                The user has asked about something outside of ecommerce/shopping scope.
                Politely redirect them back to shopping-related topics while being understanding.
                
                Your response should:
                1. Acknowledge their question politely
                2. Explain that you're focused on ecommerce assistance
                3. Redirect to what you CAN help with
                4. Ask if there's anything shopping-related you can assist with
                
                Be friendly and helpful, not dismissive. Make the redirect feel natural.
                Always reply in markdown.
                """),
            ("user", "{message}"),
            ("user", "{conversation_context}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(out_of_scope_prompt.invoke({"message": user_message, "conversation_context": conversation_context}))
        return str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
    except Exception:
        return """I appreciate your question, but I'm specifically designed to help with ecommerce and shopping-related tasks. I can't assist with topics outside of our online store.

However, I'd be happy to help you with:
• Finding and searching for products
• Managing your shopping cart
• Placing orders and payments
• Account and address management
• Order tracking and history
• General shopping questions

Is there anything shopping-related I can help you with today?"""

async def _handle_smalltalk(user_message: str, state: GlobalState = None) -> str:
    """Handle casual conversation with ecommerce focus."""
    try:
        # Get conversation context
        conversation_context = format_conversation_context_with_template(
            state=dict(state) if state else {},
            template_name="general",
            limit=5,
            fallback_message=""
        ) if state else ""
        
        smalltalk_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                ## Your Role

                You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter.

                ## Your Communication Style

                **Tone & Approach:**
                - Be warm and welcoming, but respect the customer's time by being efficient
                - Use conversational language that feels human, not robotic or scripted
                - Match the customer's energy level and tone
                - Use "I" and "you" to create a personal connection

                Engage in casual conversation with warmth and friendliness.
                Keep responses natural and conversational, but always steer toward shopping when appropriate.
                Be concise (1-2 sentences) and maintain a helpful, professional tone.
                Always reply in markdown.
                """),
            ("user", "{message}"),
            ("user", "{conversation_context}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(smalltalk_prompt.invoke({"message": user_message, "conversation_context": conversation_context}))
        return str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
    except Exception:
        return "I'm doing well, thank you! I'm here to help you with all your shopping needs. What can I assist you with today?"

async def _handle_faq(user_message: str, state: GlobalState = None) -> str:
    """Handle frequently asked questions with comprehensive ecommerce info."""
    try:
        # Get conversation context
        conversation_context = format_conversation_context_with_template(
            state=dict(state) if state else {},
            template_name="general",
            limit=5,
            fallback_message=""
        ) if state else ""
        
        faq_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                ## Your Role

                You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter.

                ## Your Capabilities

                You can assist customers with:
                - Explaining company policies (shipping, returns, warranties, etc.)
                - Answering questions about features, specifications, sizing, and availability
                - Providing information about orders and delivery

                ## Your Communication Style

                **Language Guidelines:**
                - Keep responses clear, concise, and easy to understand
                - Avoid jargon unless the customer uses it first
                - Use positive framing ("Here's what I can do..." instead of "I can't do that, but...")
                - Break complex information into digestible chunks

                Answer frequently asked questions with clear, helpful information about these topics:
                
                **Shipping & Delivery:**
                - Standard shipping (3-5 business days)
                - Express shipping options available
                - Free shipping on orders over certain amounts
                - Tracking information provided
                
                **Returns & Refunds:**
                - 30-day return policy
                - Items must be in original condition
                - Easy return process through your account
                - Refunds processed within 5-7 business days
                
                **Payment Methods:**
                - Credit/debit cards accepted
                - Secure payment processing
                - Cash on delivery available in select areas
                
                **Account Management:**
                - Create account for faster checkout
                - Save multiple addresses
                - Track order history
                - Manage preferences
                
                If the question doesn't match these topics, provide a helpful general response and suggest they contact support for specific issues.
                Always reply in markdown.
                """),
            ("user", "{message}"),
            ("user", "{conversation_context}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(faq_prompt.invoke({"message": user_message, "conversation_context": conversation_context}))
        return str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
    except Exception:
        return "I'd be happy to help answer your questions about shipping, returns, payments, or account management. What specific information would you like to know?"

async def _handle_support_query(user_message: str, state: GlobalState = None) -> str:
    """Handle customer support queries with ecommerce focus."""
    try:
        # Get conversation context
        conversation_context = format_conversation_context_with_template(
            state=dict(state) if state else {},
            template_name="general",
            limit=5,
            fallback_message=""
        ) if state else ""
        
        support_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                ## Your Role

                You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter.

                ## Your Capabilities

                You can assist customers with:
                - Tracking shipments and providing delivery updates
                - Handling returns, exchanges, and refunds
                - Troubleshooting issues with orders or accounts
                - Answering questions about features, specifications, sizing, and availability

                ## Your Communication Style

                **Empathy & Understanding:**
                - Acknowledge customer emotions and concerns ("I understand how frustrating that must be...")
                - Show genuine care when customers face issues ("Let me make this right for you")
                - Be patient with questions, no matter how many times they're asked

                ## Problem-Solving Approach

                When customers face issues:
                1. **Acknowledge** - Validate their concern immediately
                2. **Apologize** - When appropriate, offer a sincere apology on behalf of the company
                3. **Act** - Provide a clear solution or next step
                4. **Assure** - Confirm the issue is resolved or being handled

                Provide empathetic, solution-focused help for these common issues:
                
                **Order Issues:**
                - Order status and tracking
                - Delivery problems
                - Order modifications or cancellations
                - Missing or damaged items
                
                **Account Problems:**
                - Login difficulties
                - Password reset
                - Profile updates
                - Address management
                
                **Payment Issues:**
                - Payment failures
                - Refund status
                - Billing questions
                
                **Product Questions:**
                - Product availability
                - Product specifications
                - Compatibility questions
                
                Always be understanding and offer practical next steps. If you can't resolve the issue directly, guide them to the appropriate workflow or suggest contacting specialized support.
                Always reply in markdown.
                """),
            ("user", "{message}"),
            ("user", "{conversation_context}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(support_prompt.invoke({"message": user_message, "conversation_context": conversation_context}))
        return str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
    except Exception:
        return "I understand you need support, and I'm here to help! Could you please provide more details about the issue you're experiencing? I can assist with orders, account problems, payments, or product questions."

async def _handle_unknown(user_message: str, state: GlobalState = None) -> str:
    """Handle unclear or ambiguous requests."""
    try:
        # Get conversation context
        conversation_context = format_conversation_context_with_template(
            state=dict(state) if state else {},
            template_name="general",
            limit=5,
            fallback_message=""
        ) if state else ""
        
        unknown_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                ## Your Role

                You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter.

                ## Your Communication Style

                **Language Guidelines:**
                - Keep responses clear, concise, and easy to understand
                - Use positive framing ("Here's what I can do..." instead of "I can't do that, but...")
                - Break complex information into digestible chunks

                **Proactive Assistance:**
                - Provide complete information upfront to minimize back-and-forth
                - Suggest next steps to keep the customer's journey moving forward

                The user's message wasn't clearly understood. Provide a helpful response that:
                1. Politely acknowledges you didn't fully understand
                2. Asks for clarification in a friendly way
                3. Suggests specific ecommerce actions they might want to take
                4. Maintains a helpful, professional tone
                
                Always include concrete examples of what you can help with to guide the user.
                Always reply in markdown.
                """),
            ("user", "{message}"),
            ("user", "{conversation_context}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(unknown_prompt.invoke({"message": user_message, "conversation_context": conversation_context}))
        return str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
    except Exception:
        return await _get_default_ecommerce_response(user_message, state)

async def _get_default_ecommerce_response(user_message: str = "", state: GlobalState = None) -> str:
    """Provide a safe default response when all else fails."""
    try:
        # Get conversation context
        conversation_context = format_conversation_context_with_template(
            state=dict(state) if state else {},
            template_name="general",
            limit=5,
            fallback_message=""
        ) if state else ""
        
        default_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                # System Prompt - Role Section for E-commerce Chatbot

                ## Your Role

                You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter.

                ## Your Communication Style

                **Language Guidelines:**
                - Keep responses clear, concise, and easy to understand
                - Use positive framing ("Here's what I can do..." instead of "I can't do that, but...")
                - Break complex information into digestible chunks

                **Proactive Assistance:**
                - Provide complete information upfront to minimize back-and-forth
                - Suggest next steps to keep the customer's journey moving forward

                The user's request wasn't clearly understood or an error occurred.
                Provide a helpful, apologetic response that:
                1. Politely acknowledges the confusion
                2. Asks for clarification
                3. Lists specific ecommerce tasks you can help with
                4. Encourages them to try again with examples
                
                Be friendly, professional, and helpful. Make it easy for them to know what to ask for.
                
                You can help with:
                • Searching for products
                • Managing cart and orders
                • Account and address management
                • Payment and checkout assistance
                • General shopping questions
                """),
            ("user", "{message}"),
            ("user", "{conversation_context}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(default_prompt.invoke({"message": user_message, "conversation_context": conversation_context}))
        return str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
    except Exception:
        return """I'm not sure I understood that correctly. Could you please rephrase your request?

I'm here to help you with:
• Searching for products
• Managing your cart and orders
• Account and address management
• Payment and checkout assistance
• General shopping questions

What would you like to do today?"""
