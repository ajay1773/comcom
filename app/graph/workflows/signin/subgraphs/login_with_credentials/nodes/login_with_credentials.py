from typing import cast
from langchain_core.prompts import ChatPromptTemplate
from app.graph.workflows.signin.types import LoginWithCredentialsState
from app.services.db.user import user_service
from app.services.password import PasswordService
from app.services.llm import llm_service
from app.services.jwt import JWTService


async def login_with_credentials_node(state: LoginWithCredentialsState) -> LoginWithCredentialsState:
    """Login with credentials and verify password."""
    
    llm = llm_service.get_llm_without_tools()
    user = state.get("user")
    credentials = state.get("credentials", {})
    
    if user and credentials:
        try:
            # Get the stored password hash
            stored_password_hash = await user_service.get_password_hash(user.email)
            provided_password = credentials.get("password", "")
            
            # Verify password
            if stored_password_hash and PasswordService.verify_password(provided_password, stored_password_hash):
                # Successful login
                success_prompt_template = ChatPromptTemplate.from_messages([
                    ("system", """
                    You are an e-commerce system.
                        Generate ONLY one short, friendly sentence that:
                        1. Welcomes the user back and confirms successful login.
                        2. Does not include technical words (like 'query', 'results', 'response').
                        3. Does not include email, password, or any sensitive details.
                        4. Does not add extra instructions like "let us know if you need help" or "best regards".
                        5. Keeps the tone conversational, natural, and concise.
                        6. End the message by suggesting they can start browsing or looking for what they want.

                        Output must be a single sentence, nothing else.
                    """,),
                    ("user", "User has successfully logged in with email: {email}")
                ])
                success_prompt = await llm.ainvoke(success_prompt_template.invoke({"email": user.email}))
                jwt_token = await JWTService.generate_jwt(user.id) if user.id else None
                state['suggestions'] = [cast(str, success_prompt)]
                state['workflow_widget_json'] = {
                    "template": "login_success",
                    "payload": {
                        "message": success_prompt,
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "first_name": user.first_name,
                            "last_name": user.last_name
                        },
                        'jwt_token': jwt_token
                    }
                }
                
                # Set authentication state
                state["is_authenticated"] = True
                state["user_id"] = user.id
                
            else:
                # Invalid password
                failure_prompt_template = ChatPromptTemplate.from_messages([
                    ("system", """You are an e-commerce system. Generate a short, friendly message that: 
                    1. Politely informs the user that the password is incorrect. 
                    2. Do not use technical words like 'query', 'results', or 'response'. 
                    3. Keeps the tone conversational and natural, as if chatting with a human. 
                    4. Suggest they try again or reset their password.
                    5. Do not send the email or password in the message back to the user.
                    6. Simply tell the user that the password is incorrect and suggest them to try again or reset their password.""",),
                    ("user", "User provided incorrect password for email: {email}")
                ])
                failure_prompt = await llm.ainvoke(failure_prompt_template.invoke({"email": credentials.get("email", "")}))
                
                state['suggestions'] = [cast(str, failure_prompt)]
                state['workflow_widget_json'] = {
                    "template": "login_failure",
                    "payload": {
                        "message": failure_prompt,
                        "reason": "invalid_password"
                    }
                }
                
        except Exception:
            # Handle any errors during login
            error_prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an e-commerce system. Generate a short, friendly message that: 
                1. Politely informs the user that login failed due to a technical issue. 
                2. Do not use technical words like 'query', 'results', or 'response'. 
                3. Keeps the tone conversational and natural, as if chatting with a human. 
                4. Suggest they try again later.
                5. Do not send the email or password in the message back to the user.
                6. Simply tell the user that login failed due to a technical issue and suggest them to try again later.""",),
                ("user", "Login failed due to technical error")
            ])
            error_prompt = await llm.ainvoke(error_prompt_template.invoke({}))
            
            state['suggestions'] = [cast(str, error_prompt)]
            state['workflow_widget_json'] = {
                "template": "login_error",
                "payload": {
                    "message": error_prompt
                }
            }
    else:
        # No user found
        no_user_prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an e-commerce system. Generate a short, friendly message that: 
            1. Politely informs the user that no account exists with the provided email. 
            2. Do not use technical words like 'query', 'results', or 'response'. 
            3. Keeps the tone conversational and natural, as if chatting with a human. 
            4. Do not use any exclamation marks.
            5. Suggest they sign up for a new account or try again.
            6. Do not send the email or password in the message back to the user.
            """),
            ("user", "No user found with email: {email}"),
        ])
        no_user_prompt = await llm.ainvoke(no_user_prompt_template.invoke({"email": credentials.get("email", "")}))
        
        state['suggestions'] = [cast(str, no_user_prompt)]
        state['workflow_widget_json'] = {
            "template": "login_failure",
            "payload": {
                "message": no_user_prompt,
                "reason": "user_not_found"
            }
        }
    
    return state
