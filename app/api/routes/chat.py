from typing import cast
from fastapi import APIRouter, Request
from app.models.chat import ChatRequest, ChatResponse
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app.services.stream import stream_service
from app.services.monitoring import monitoring_service
from app.services.langgraph_history import langgraph_history_service
from app.services.rate_limiter import rate_limiter_service, RateLimitError
from app.services.auth import auth_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat")
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Simple chat endpoint that returns a response.

    Args:
        request: The chat request containing the query and optional session ID
    Returns:
        Chat response
    """
    # Simple echo response for demonstration
    return ChatResponse(response=f"You said: {request.query}", done=True)


@router.post("/chat/stream")
async def stream_chat(request: ChatRequest, http_request: Request):
    """
    Stream chat response endpoint with rate limiting.
    
    Rate Limits:
    - Logged-out users: 20 requests per hour (IP-based)
    - Logged-in users: 100,000 tokens per day
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Extract token and client IP
        token = cast(str, http_request.headers.get("Authorization")).split(" ")[1] if http_request.headers.get("Authorization") else ''
        client_ip = http_request.client.host if http_request.client else "unknown"
        
        # Determine if user is authenticated
        user = None
        is_authenticated = False
        
        if token:
            try:
                user = await auth_service.get_user_from_token(token)
                if user:
                    is_authenticated = True
                    logger.info(f"Authenticated request from user {user.id}")
            except Exception as e:
                logger.warning(f"Token validation failed: {e}")
        
        # Apply rate limiting based on authentication status
        if is_authenticated and user and user.id:
            # Check token usage limit for logged-in users
            token_status = await rate_limiter_service.check_token_limit_for_user(user.id)
            
            if not token_status["allowed"]:
                # Token limit exceeded
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Daily token limit exceeded",
                        "message": "You have reached your daily token usage limit. Your limit will reset tomorrow.",
                        "tokens_used": token_status["tokens_used"],
                        "daily_limit": token_status["daily_limit"],
                        "reset_date": token_status["reset_date"],
                        "limit_type": "tokens"
                    }
                )
            
            logger.info(f"User {user.id} has {token_status['remaining_tokens']} tokens remaining today")
            
        else:
            # Check request rate limit for logged-out users (IP-based)
            try:
                rate_limit_status = await rate_limiter_service.check_rate_limit_for_ip(client_ip)
                logger.info(f"IP {client_ip} has {rate_limit_status['remaining_requests']} requests remaining")
                
            except RateLimitError as e:
                # Rate limit exceeded for logged-out user
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": e.message,
                        "retry_after": e.retry_after,
                        "limit_type": "requests",
                        "suggestion": "Please sign in to continue chatting with higher limits."
                    }
                )
        
        # Rate limit checks passed - proceed with streaming
        return StreamingResponse(
            stream_service.stream_base_graph_with_token_tracking(
                message=request.query, 
                thread_id=request.thread_id or "", 
                token=token,
                user_id=user.id if user else None
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in stream_chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        health_status = monitoring_service.get_health_status()
        return health_status
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "unknown"
        }


@router.get("/chat/history/{thread_id}")
async def get_chat_history(thread_id: str):
    """
    Get conversation message history from LangGraph checkpointer.
    
    This endpoint retrieves the actual conversation messages stored in LangGraph's
    checkpointer database by connecting to the same SQLite database that LangGraph
    uses for state persistence.
    
    Args:
        thread_id: The LangGraph thread identifier
        
    Returns:
        dict: Contains messages array with conversation history
        
    Raises:
        404: Thread not found in checkpointer
        500: Internal server error
    """
    try:
        # Check if thread exists
        if not await langgraph_history_service.thread_exists(thread_id):
            raise HTTPException(
                status_code=404,
                detail=f"Thread {thread_id} not found in conversation history"
            )
        
        # Retrieve conversation history from LangGraph checkpointer
        messages = await langgraph_history_service.get_conversation_history(thread_id)
        
        return {
            "messages": messages,
            "thread_id": thread_id,
            "total_messages": len(messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_chat_history: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve chat history: {str(e)}"
        )


@router.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    try:
        return monitoring_service.metrics.get_all_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/rate-limit/status")
async def get_rate_limit_status(http_request: Request):
    """
    Get rate limit status for the current user/IP.
    
    Returns:
        For logged-in users: Token usage and remaining quota
        For logged-out users: Request count and remaining requests
    """
    try:
        # Extract token and client IP
        token = cast(str, http_request.headers.get("Authorization")).split(" ")[1] if http_request.headers.get("Authorization") else ''
        client_ip = http_request.client.host if http_request.client else "unknown"
        
        # Check if user is authenticated
        user = None
        if token:
            try:
                user = await auth_service.get_user_from_token(token)
            except Exception:
                pass
        
        if user and user.id:
            # Return token usage status for logged-in user
            token_status = await rate_limiter_service.get_user_token_status(user.id)
            return {
                "user_type": "authenticated",
                "user_id": user.id,
                "tokens_used": token_status["tokens_used"],
                "remaining_tokens": token_status["remaining_tokens"],
                "daily_limit": token_status["daily_limit"],
                "reset_date": token_status["reset_date"],
                "limit_type": "tokens"
            }
        else:
            # Return request rate limit status for logged-out user (READ ONLY - doesn't increment)
            rate_status = await rate_limiter_service.get_rate_limit_status_for_ip(client_ip)
            return {
                "user_type": "guest",
                "ip_address": client_ip,
                "remaining_requests": rate_status["remaining_requests"],
                "limit": rate_status["limit"],
                "reset_time": rate_status["reset_time"],
                "limit_exceeded": rate_status.get("limit_exceeded", False),
                "retry_after": rate_status.get("retry_after"),
                "limit_type": "requests"
            }
                
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get rate limit status: {str(e)}")
