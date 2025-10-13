from typing import cast
from langchain_core.prompts import ChatPromptTemplate
from app.graph.workflows.signin.types import LoginWithCredentialsState
from app.services.db.user import user_service
from app.services.password import PasswordService
from app.services.llm import llm_service
from app.services.jwt import JWTService
from app.services.auth import auth_service
from app.services.widget_events import widget_event_emitter, WidgetEventType
from app.types.common import BASE_PERSONA_PROMPT
from app.utils.conversation_context import format_conversation_context_with_template


async def login_with_credentials_node(state: LoginWithCredentialsState) -> LoginWithCredentialsState:
    """Login with credentials and verify password."""
    
    llm = llm_service.get_llm_without_tools()
    user = state.get("user")
    credentials = state.get("credentials", {})
    thread_id = state.get("thread_id", "")
    conversation_context = format_conversation_context_with_template(
        state=dict(state),
        template_name="general",
        limit=5,
        fallback_message=""
    )
    
    if user and credentials:
        try:
            # Get the stored password hash
            stored_password_hash = await user_service.get_password_hash(user.email)
            provided_password = credentials.get("password", "")
            
            # Verify password
            if stored_password_hash and PasswordService.verify_password(provided_password, stored_password_hash):
                # Successful login
                success_prompt_template = ChatPromptTemplate.from_messages([
                    ("system", BASE_PERSONA_PROMPT + """
                    ###TASK:
                    - Welcomes the user back and confirms successful login.

                    ###RULES:
                    - Does not include technical words (like 'query', 'results', 'response').
                    - Does not include email, password, or any sensitive details.
                    - Does not add extra instructions like "let us know if you need help" or "best regards".
                    - Keeps the tone conversational, natural, and concise.
                    - End the message by suggesting they can start browsing or looking for what they want.
                    """,),
                    ("assistant", "{conversation_context}"),
                    ("user", "User has successfully logged in with email: {email}"),
                ])
                success_prompt = await llm.ainvoke(success_prompt_template.invoke({"email": user.email, "conversation_context": conversation_context}))
                
                # Create session in database (for conversation management)
                session_token = None
                if user.id and thread_id:
                    try:
                        session_token = await auth_service.create_session(user.id, thread_id)
                        print(f"✅ Created session for user {user.id} with thread {thread_id}")
                    except Exception as e:
                        print(f"⚠️ Failed to create session: {e}")
                        # Continue with JWT-only approach if session creation fails
                
                # Generate JWT token (for API authentication)
                jwt_token = await JWTService.generate_jwt(user.id) if user.id else None
                
                # Use session token if available, otherwise use JWT token
                auth_token = session_token if session_token else jwt_token
                
                state['suggestions'] = [cast(str, success_prompt)]
                widget_event_emitter.emit(
                    WidgetEventType.SIGNIN_SUCCESS,
                    {
                        "jwt_token": auth_token,  # Send session token or JWT token
                        "user": user,
                        "suggested_actions": ["Continue shopping"]
                    }
                )
                
                # Set authentication state
                state["is_authenticated"] = True
                state["user_id"] = user.id
                
            else:
                # Invalid password
                failure_prompt_template = ChatPromptTemplate.from_messages([
                    ("system", BASE_PERSONA_PROMPT + """
                    ###TASK:
                    - Politely informs the user that the password is incorrect.

                    ###RULES:
                    - Do not use technical words like 'query', 'results', or 'response'.
                    - Keeps the tone conversational and natural, as if chatting with a human.
                    - Suggest they try again or reset their password.
                    - Do not tell user to use the forget password feature as that is not a feature of the system.
                    """,),
                    ("assistant", "{conversation_context}"),
                    ("user", "User provided incorrect password for email: {email}")
                ])
                failure_prompt = await llm.ainvoke(failure_prompt_template.invoke({"email": credentials.get("email", ""), "conversation_context": conversation_context}))
                
                state['suggestions'] = [cast(str, failure_prompt)]
                widget_event_emitter.emit(
                    WidgetEventType.SIGNIN_FAILURE,
                    {
                        "message": failure_prompt,
                        "reason": "invalid_password",
                    }
                )
                
        except Exception:
            # Handle any errors during login
            error_prompt_template = ChatPromptTemplate.from_messages([
                ("system", BASE_PERSONA_PROMPT + """
                ###TASK:
                - Politely informs the user that login failed due to a technical issue.

                ###RULES:
                - Do not use technical words like 'query', 'results', or 'response'.
                - Keeps the tone conversational and natural, as if chatting with a human.
                - Suggest they try again later.
                - Do not send the email or password in the message back to the user.
                - Do not tell user to use the forget password feature as that is not a feature of the system.
                """,),
                ("assistant", "{conversation_context}"),
                ("user", "Login failed due to technical error")
            ])
            error_prompt = await llm.ainvoke(error_prompt_template.invoke({"conversation_context": conversation_context}))
            
            state['suggestions'] = [cast(str, error_prompt)]
            widget_event_emitter.emit(
                WidgetEventType.SIGNIN_FAILURE,
                {
                    "message": error_prompt,
                    "reason": "technical_error",
                }
            )
    else:
        # No user found
        no_user_prompt_template = ChatPromptTemplate.from_messages([
            ("system", BASE_PERSONA_PROMPT + """
            ###TASK:
            - Politely informs the user that no account exists with the provided email.

            ###RULES:
            - Do not use technical words like 'query', 'results', or 'response'.
            - Keeps the tone conversational and natural, as if chatting with a human.
            - Suggest they sign up for a new account or try again.
            - Do not send the email or password in the message back to the user.
            - Do not tell user to use the forget password feature as that is not a feature of the system.
            """,),
            ("assistant", "{conversation_context}"),
            ("user", "No user found with email: {email}"),
        ])
        no_user_prompt = await llm.ainvoke(no_user_prompt_template.invoke({"email": credentials.get("email", ""), "conversation_context": conversation_context}))
        
        state['suggestions'] = [cast(str, no_user_prompt)]
        widget_event_emitter.emit(
            WidgetEventType.SIGNIN_FAILURE,
            {
                "message": no_user_prompt,
                "reason": "user_not_found",
            }
        )
    
    return state
