from typing import cast
from langchain_core.prompts import ChatPromptTemplate
from app.graph.workflows.signup.types import SignupWithDetailsState
from app.services.db.user import user_service
from app.services.password import PasswordService
from app.models.user import UserCreate
from app.services.llm import llm_service
from app.services.db.cart import cart_service
import logging


logger = logging.getLogger(__name__)

async def save_user_details_node(state: SignupWithDetailsState) -> SignupWithDetailsState:
    """Save user details."""

    llm = llm_service.get_llm_without_tools()
    user = state.get("details")    
    if user:
        try:
            # Validate required fields exist
            email = user.get("email")
            password = user.get("password")
            first_name = user.get("first_name")
            last_name = user.get("last_name")
            phone = user.get("phone")
            
            if not all([email, password, first_name, last_name, phone]):
                raise ValueError("Missing required user details")
            
            user_details = UserCreate(
                email=str(email),
                password=str(password),
                first_name=str(first_name),
                last_name=str(last_name),
                phone=str(phone)
            )
            new_user_id = await user_service.create_user(user_data=user_details, password_hash=PasswordService.hash_password(str(password)))
            if not new_user_id:
                raise ValueError("Failed to create user")
            
            await cart_service.get_or_create_cart(user_id=new_user_id)
            
            success_prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an e-commerce system. Generate a short, friendly message that: 
                1. Politely informs the user that they have been successfully signed up. 
                2. Do not use technical words like 'query', 'results', or 'response'. 
                3. Keeps the tone conversational and natural, as if chatting with a human. 
                4. Do not use any exclamation marks.
                5. Tell the user that they can now sign in to their account.
                6. Do not use terms that indicate user that they have joined some kind of community or group or club or anything like that.
                7. Keep in mind that the UI for signin will be shown in the side of the chat-window so do not ask user to go to any page and signin in there. 
                """),
                ("user", "User: {user_message}")
            ])
            success_prompt = await llm.ainvoke(success_prompt_template.invoke({"user_message": "User has been successfully signed up."}))
            state['suggestions'] = [cast(str, success_prompt)]
            state['workflow_widget_json'] = {
                "template": "signup_success",
                "payload": {
                    "message": success_prompt
                }
            }

        except Exception as e:
                logger.error(f"Error saving user details: {e}", extra={"user_message": state.get("user_message", "")})
                failure_prompt_template = ChatPromptTemplate.from_messages([
                    ("system", """You are an e-commerce system. Generate a short, friendly message that: 
                    1. Politely informs the user that the signup failed. 
                    2. Do not use technical words like 'query', 'results', or 'response'. 
                    3. Keeps the tone conversational and natural, as if chatting with a human. 
                    4. Find out what went wrong and tell the user the reason.
                        For example if error is "UNIQUE constraint failed: users.email" then tell the user that the email is already in use.
                    5. Tell the user that they can try again later.
                    6. Do not use terms that indicate user that they have joined some kind of community or group or club or anything like that."""),
                    ("user", "Error: {error}"),
                    ("user", "User: {user_message}")
                ])
                response = await llm.ainvoke(failure_prompt_template.invoke({"user_message": "Signup has failed.", "error": e}))
                state['suggestions'] = [cast(str, response)]
                state['workflow_widget_json'] = {
                    "template": "signup_failure",
                    "payload": {
                        "message": response
                    }
                }
    return state
