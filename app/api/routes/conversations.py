"""
API routes for conversation management.

This module provides REST endpoints for managing user conversations including:
- Listing user conversations with filtering and pagination
- Retrieving specific conversations by ID
- Updating conversation metadata (title, archive status, favorite status)
- Deleting conversations

All endpoints support both authenticated and anonymous users, with proper
access control to ensure users can only access their own conversations.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from app.services.db.conversation import conversation_service, Conversation
from app.services.auth import auth_service


router = APIRouter()


class ConversationResponse(BaseModel):
    """
    Response model for conversation data.
    
    Attributes:
        id: Unique conversation identifier
        thread_id: LangGraph thread identifier for conversation state
        user_id: ID of the user who owns this conversation (null for anonymous)
        title: Human-readable conversation title (auto-generated or user-set)
        created_at: ISO timestamp when conversation was created
        updated_at: ISO timestamp when conversation was last modified
        last_message_at: ISO timestamp of the last message in conversation
        message_count: Total number of messages in the conversation
        is_archived: Whether the conversation is archived
        is_favorite: Whether the conversation is marked as favorite
    """
    id: int
    thread_id: str
    user_id: int | None
    title: str | None
    created_at: str | None
    updated_at: str | None
    last_message_at: str | None
    message_count: int
    is_archived: bool
    is_favorite: bool


class ConversationListResponse(BaseModel):
    """
    Response model for conversation list with pagination info.
    
    Attributes:
        conversations: List of conversation objects
        total_count: Total number of conversations matching the query
    """
    conversations: List[ConversationResponse]
    total_count: int


class ConversationUpdateRequest(BaseModel):
    """
    Request model for updating conversation metadata.
    
    All fields are optional - only provided fields will be updated.
    
    Attributes:
        title: New title for the conversation
        is_archived: Archive status (true to archive, false to unarchive)
        is_favorite: Favorite status (true to favorite, false to unfavorite)
    """
    title: Optional[str] = None
    is_archived: Optional[bool] = None
    is_favorite: Optional[bool] = None


def conversation_to_response(conv: Conversation) -> ConversationResponse:
    """
    Convert internal Conversation model to API response model.
    
    Args:
        conv: Internal conversation model from database
        
    Returns:
        ConversationResponse: API-formatted conversation data
    """
    return ConversationResponse(
        id=conv.id or 0,
        thread_id=conv.thread_id,
        user_id=conv.user_id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        last_message_at=conv.last_message_at,
        message_count=conv.message_count,
        is_archived=conv.is_archived,
        is_favorite=conv.is_favorite
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def get_user_conversations(
    include_archived: bool = Query(False, description="Include archived conversations in results"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip for pagination"),
    search: Optional[str] = Query(None, description="Search term to filter conversations by title"),
    current_user = Depends(auth_service.get_current_user_optional)
):
    """
    Get all conversations for the current user.
    
    This endpoint returns a paginated list of conversations belonging to the authenticated user.
    Anonymous users will receive an empty list. Conversations are ordered by last activity
    (most recent first).
    
    Query Parameters:
        - include_archived: Whether to include archived conversations (default: false)
        - limit: Maximum conversations to return (1-100, default: 50)
        - offset: Number of conversations to skip for pagination (default: 0)
        - search: Filter conversations by title containing this text (requires authentication)
    
    Returns:
        ConversationListResponse: List of conversations with pagination info
        
    Raises:
        401: Authentication required for search functionality
        500: Internal server error
    """
    try:
        user_id = current_user.id if current_user else None
        
        if search and not user_id:
            raise HTTPException(
                status_code=401, 
                detail="Authentication required for search functionality"
            )
        
        if user_id:
            conversations = await conversation_service.get_user_conversations(
                user_id=user_id,
                include_archived=include_archived
            )
            
            # Apply search filter if provided
            if search:
                conversations = [
                    conv for conv in conversations 
                    if conv.title and search.lower() in conv.title.lower()
                ]
            
            # Apply pagination
            total_count = len(conversations)
            conversations = conversations[offset:offset + limit]
        else:
            # Anonymous users get empty list
            conversations = []
            total_count = 0
        
        return ConversationListResponse(
            conversations=[conversation_to_response(conv) for conv in conversations],
            total_count=total_count
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve conversations: {str(e)}"
        )


@router.get("/conversations/id/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_by_id(
    conversation_id: int,
    current_user = Depends(auth_service.get_current_user_optional)
):
    """
    Get a specific conversation by its unique ID.
    
    This endpoint retrieves detailed information about a single conversation.
    Users can only access conversations they own, or anonymous conversations
    if they are not authenticated.
    
    Path Parameters:
        conversation_id: Unique identifier of the conversation to retrieve
    
    Returns:
        ConversationResponse: Detailed conversation information
        
    Raises:
        403: Access denied - user doesn't own this conversation
        404: Conversation not found
        500: Internal server error
    """
    try:
        conversation = await conversation_service.get_conversation_by_id(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=404, 
                detail="Conversation not found"
            )
        
        # Access control: users can only access their own conversations
        # Anonymous users can access conversations without a user_id
        if (current_user and conversation.user_id and 
            conversation.user_id != current_user.id):
            raise HTTPException(
                status_code=403, 
                detail="Access denied - you don't have permission to view this conversation"
            )
        
        return conversation_to_response(conversation)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve conversation: {str(e)}"
        )


@router.put("/conversations/id/{conversation_id}", response_model=ConversationResponse)
async def update_conversation_by_id(
    conversation_id: int,
    update_data: ConversationUpdateRequest,
    current_user = Depends(auth_service.get_current_user_optional)
):
    """
    Update conversation metadata by conversation ID.
    
    This endpoint allows updating various metadata fields of a conversation including
    title, archive status, and favorite status. Only the conversation owner can
    make updates.
    
    Path Parameters:
        conversation_id: Unique identifier of the conversation to update
        
    Request Body:
        ConversationUpdateRequest: Fields to update (all optional)
        - title: New conversation title
        - is_archived: Archive status (true/false)
        - is_favorite: Favorite status (true/false)
    
    Returns:
        ConversationResponse: Updated conversation data
        
    Raises:
        403: Access denied - user doesn't own this conversation
        404: Conversation not found
        500: Internal server error
    """
    try:
        conversation = await conversation_service.get_conversation_by_id(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=404, 
                detail="Conversation not found"
            )
        
        # Access control: only conversation owner can update
        if (current_user and conversation.user_id and 
            conversation.user_id != current_user.id):
            raise HTTPException(
                status_code=403, 
                detail="Access denied - you don't have permission to update this conversation"
            )
        
        # Update fields if provided
        if update_data.title is not None:
            await conversation_service.update_conversation_title(
                conversation.thread_id, 
                update_data.title
            )
        
        if update_data.is_archived is not None:
            await conversation_service.archive_conversation(
                conversation.thread_id, 
                update_data.is_archived
            )
        
        if update_data.is_favorite is not None:
            await conversation_service.favorite_conversation(
                conversation.thread_id, 
                update_data.is_favorite
            )
        
        # Return updated conversation
        updated_conversation = await conversation_service.get_conversation_by_id(conversation_id)
        
        if not updated_conversation:
            raise HTTPException(
                status_code=500, 
                detail="Failed to retrieve updated conversation"
            )
        
        return conversation_to_response(updated_conversation)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to update conversation: {str(e)}"
        )


@router.delete("/conversations/id/{conversation_id}")
async def delete_conversation_by_id(
    conversation_id: int,
    current_user = Depends(auth_service.get_current_user_optional)
):
    """
    Delete a conversation permanently by conversation ID.
    
    This endpoint permanently removes a conversation and all its associated data.
    Only the conversation owner can delete their conversations. This action
    cannot be undone.
    
    Path Parameters:
        conversation_id: Unique identifier of the conversation to delete
    
    Returns:
        dict: Success message confirming deletion
        
    Raises:
        403: Access denied - user doesn't own this conversation
        404: Conversation not found
        500: Internal server error
    """
    try:
        conversation = await conversation_service.get_conversation_by_id(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=404, 
                detail="Conversation not found"
            )
        
        # Access control: only conversation owner can delete
        if (current_user and conversation.user_id and 
            conversation.user_id != current_user.id):
            raise HTTPException(
                status_code=403, 
                detail="Access denied - you don't have permission to delete this conversation"
            )
        
        await conversation_service.delete_conversation(conversation.thread_id)
        
        return {"message": "Conversation deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete conversation: {str(e)}"
        )


@router.post("/conversations/id/{conversation_id}/regenerate-title", response_model=ConversationResponse)
async def regenerate_conversation_title(
    conversation_id: int,
    current_user = Depends(auth_service.get_current_user_optional)
):
    """
    Regenerate conversation title using LLM based on current conversation history.
    
    This endpoint analyzes the conversation history and generates a new, more
    descriptive title using AI. Only the conversation owner can regenerate titles.
    
    Path Parameters:
        conversation_id: Unique identifier of the conversation to update
    
    Returns:
        ConversationResponse: Updated conversation data with new title
        
    Raises:
        403: Access denied - user doesn't own this conversation
        404: Conversation not found
        500: Internal server error
    """
    try:
        conversation = await conversation_service.get_conversation_by_id(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=404, 
                detail="Conversation not found"
            )
        
        # Access control: only conversation owner can regenerate title
        if (current_user and conversation.user_id and 
            conversation.user_id != current_user.id):
            raise HTTPException(
                status_code=403, 
                detail="Access denied - you don't have permission to update this conversation"
            )
        
        # Regenerate title using conversation history
        new_title = await conversation_service.regenerate_conversation_title(conversation.thread_id)
        
        # Return updated conversation
        updated_conversation = await conversation_service.get_conversation_by_id(conversation_id)
        
        if not updated_conversation:
            raise HTTPException(
                status_code=500, 
                detail="Failed to retrieve updated conversation"
            )
        
        return conversation_to_response(updated_conversation)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to regenerate conversation title: {str(e)}"
        )


# ============================================================================
# API ENDPOINTS SUMMARY
# ============================================================================
#
# This module provides 5 essential REST endpoints for conversation management:
#
# 1. GET /conversations
#    - Lists all conversations for the authenticated user
#    - Supports pagination (limit, offset) and search filtering
#    - Anonymous users receive empty list
#    - Query params: include_archived, limit, offset, search
#
# 2. GET /conversations/id/{conversation_id}
#    - Retrieves a specific conversation by its unique ID
#    - Access control: users can only view their own conversations
#    - Used for URL-based conversation loading
#
# 3. PUT /conversations/id/{conversation_id}
#    - Updates conversation metadata (title, archive, favorite status)
#    - Access control: only conversation owner can update
#    - Supports partial updates (all fields optional)
#
# 4. DELETE /conversations/id/{conversation_id}
#    - Permanently deletes a conversation and all associated data
#    - Access control: only conversation owner can delete
#    - Cannot be undone
#
# 5. POST /conversations/id/{conversation_id}/regenerate-title
#    - Regenerates conversation title using LLM based on conversation history
#    - Access control: only conversation owner can regenerate title
#    - Uses actual message history from LangGraph for intelligent title generation
#
# All endpoints:
# - Support both authenticated and anonymous users with proper access control
# - Return consistent error responses (403, 404, 500)
# - Use conversation IDs for URL-based routing (not thread IDs)
# - Include comprehensive documentation and type hints
#
# Note: Conversation history is handled by /api/chat/history/{thread_id}
# in the chat routes module, not here.
# ============================================================================
