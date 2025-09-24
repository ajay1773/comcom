"""Pure function auth middleware service - no LangGraph subgraph."""

from typing import Callable
from app.models.chat import GlobalState
from app.services.jwt import JWTService
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from app.core.enums import WorkflowType
import logging

logger = logging.getLogger(__name__)


class AuthMiddlewareService:
    """Pure function auth middleware - reusable, decoupled, robust."""
    
    def __init__(self):
        self.jwt_service = JWTService
        self.llm_service = llm_service
    
    async def validate_and_execute(
        self,
        state: GlobalState,
        target_workflow: WorkflowType,
        workflow_runner: Callable,
        config: RunnableConfig | None = None
    ) -> GlobalState:
        """
        Validate authentication and execute target workflow or return auth error.
        
        Args:
            state: Global state containing session token
            target_workflow: The workflow to run after successful auth
            workflow_runner: The actual workflow function to execute
            config: Optional runnable configuration
            
        Returns:
            Updated global state with either auth error or workflow results
        """
        
        # 1. Extract and validate token
        token = state.get("session_token")
        
        if not token:
            logger.debug("No session token found")
            return await self._handle_missing_token(state, target_workflow)
        
        # 2. Parse and validate token
        try:
            token_data = await self.jwt_service.verify_jwt(token)
            user_id = token_data
            
            if not user_id:
                logger.debug("Invalid token - no user_id")
                return await self._handle_invalid_token(state, target_workflow, "Invalid token format")
                
        except Exception as e:
            logger.debug(f"Token validation failed: {e}")
            return await self._handle_invalid_token(state, target_workflow, str(e))
        
        # 3. Token is valid - update auth state and continue to target workflow
        logger.debug(f"Token valid for user_id: {user_id}, continuing to {target_workflow}")
        
        # Update global auth state
        state["is_authenticated"] = True
        state["user_id"] = user_id
        state["auth_required"] = False
        state["current_workflow"] = target_workflow.value
        state["pending_workflow"] = None
        
        # 4. Execute the target workflow
        return await workflow_runner(state, config)
    
    async def _handle_missing_token(self, state: GlobalState, target_workflow: WorkflowType) -> GlobalState:
        """Handle case where no token is provided."""
        
        # Generate friendly auth required message using LLM
        auth_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a friendly e-commerce chatbot. Generate a short, welcoming message that:
            1. Politely informs the user they need to sign in to access this feature
            2. Does not use technical words like 'token', 'authentication', 'authorization', or 'JWT'
            3. Keeps the tone conversational and helpful
            4. Mentions the specific feature they're trying to access
            5. Encourages them to sign in
            
            Output must be a single friendly sentence, nothing else.
            """),
            ("user", "User wants to access {feature} but is not signed in")
        ])
        
        try:
            llm = self.llm_service.get_llm_without_tools(disable_streaming=True)
            response = await llm.ainvoke(
                auth_prompt.invoke({
                    "feature": self._get_feature_description(target_workflow)
                })
            )
            
            auth_message = str(response.content).strip()
            
        except Exception as e:
            logger.error(f"Failed to generate auth message: {e}")
            # Fallback message
            feature = self._get_feature_description(target_workflow)
            auth_message = f"Please sign in to access {feature}. You can sign in using the login option."
        
        # Update state with auth error
        state["is_authenticated"] = False
        state["user_id"] = None
        state["auth_required"] = True
        state["pending_workflow"] = target_workflow.value
        state["response"] = auth_message
        state["workflow_output_text"] = auth_message
        
        return state
    
    async def _handle_invalid_token(self, state: GlobalState, target_workflow: WorkflowType, error: str) -> GlobalState:
        """Handle case where token is invalid or expired."""
        
        # Generate friendly session expired message using LLM
        session_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a friendly e-commerce chatbot. Generate a short, helpful message that:
            1. Politely informs the user their session has expired
            2. Does not use technical words like 'token', 'authentication', 'authorization', or 'JWT'
            3. Keeps the tone conversational and understanding
            4. Mentions the specific feature they're trying to access
            5. Encourages them to sign in again
            
            Output must be a single friendly sentence, nothing else.
            """),
            ("user", "User's session expired while trying to access {feature}")
        ])
        
        try:
            llm = self.llm_service.get_llm_without_tools(disable_streaming=True)
            response = await llm.ainvoke(
                session_prompt.invoke({
                    "feature": self._get_feature_description(target_workflow)
                })
            )
            
            session_message = str(response.content).strip()
            
        except Exception as e:
            logger.error(f"Failed to generate session message: {e}")
            # Fallback message
            feature = self._get_feature_description(target_workflow)
            session_message = f"Your session has expired. Please sign in again to access {feature}."
        
        # Update state with session error
        state["is_authenticated"] = False
        state["user_id"] = None
        state["auth_required"] = True
        state["pending_workflow"] = target_workflow.value
        state["response"] = session_message
        state["workflow_output_text"] = session_message
        
        return state
    
    def _get_feature_description(self, workflow: WorkflowType) -> str:
        """Get user-friendly description of the workflow feature."""
        descriptions = {
            WorkflowType.VIEW_CART: "your cart",
            WorkflowType.ADD_TO_CART: "add items to cart",
            WorkflowType.PLACE_ORDER: "place an order",
            WorkflowType.PRODUCT_SEARCH: "product search",
            WorkflowType.INITIATE_PAYMENT: "payment",
            WorkflowType.PAYMENT_STATUS: "payment status",
        }
        
        return descriptions.get(workflow, "this feature")


# Global instance
auth_middleware_service = AuthMiddlewareService()
