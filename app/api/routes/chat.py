from typing import cast
from fastapi import APIRouter, Request
from app.models.chat import ChatRequest, ChatResponse
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app.services.stream import stream_service
from app.services.monitoring import monitoring_service
from app.services.langgraph_history import langgraph_history_service

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
async def stream_chat(request: ChatRequest, http_request: Request
):
    """Stream chat response endpoint."""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        token = cast(str, http_request.headers.get("Authorization")).split(" ")[1] if http_request.headers.get("Authorization") else ''
        return StreamingResponse(
            stream_service.stream_base_graph(
                message=request.query, thread_id=request.thread_id or "", token=token
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
    except Exception as e:
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
