from typing import cast
from fastapi import APIRouter, Request
from app.models.chat import ChatRequest, ChatResponse
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app.services.stream import stream_service
from app.services.monitoring import monitoring_service

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
        status_code = 200 if health_status["status"] == "healthy" else 503
        return health_status
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "unknown"
        }


@router.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    try:
        return monitoring_service.metrics.get_all_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")
