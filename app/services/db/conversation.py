"""Conversation service for managing chat conversations."""

from typing import List, Optional
from datetime import datetime
from app.services.db.db import db_service, Conversation


class ConversationService:
    """Service for managing conversation operations."""

    async def create_conversation(
        self, 
        thread_id: str, 
        user_id: Optional[int] = None, 
        title: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation."""
        query = """
        INSERT INTO conversations (thread_id, user_id, title, last_message_at)
        VALUES (?, ?, ?, ?)
        RETURNING id, thread_id, user_id, title, created_at, updated_at, 
                 last_message_at, message_count, is_archived, is_favorite
        """
        
        now = datetime.now().isoformat()
        result = await db_service.execute_query(
            query, 
            (thread_id, user_id, title, now)
        )
        
        if result:
            row = result[0]
            return Conversation(
                id=row[0],
                thread_id=row[1],
                user_id=row[2],
                title=row[3],
                created_at=row[4],
                updated_at=row[5],
                last_message_at=row[6],
                message_count=row[7],
                is_archived=bool(row[8]),
                is_favorite=bool(row[9])
            )
        raise Exception("Failed to create conversation")

    async def get_conversation_by_thread_id(self, thread_id: str) -> Optional[Conversation]:
        """Get a conversation by thread ID."""
        query = """
        SELECT id, thread_id, user_id, title, created_at, updated_at,
               last_message_at, message_count, is_archived, is_favorite
        FROM conversations
        WHERE thread_id = ?
        """
        
        result = await db_service.execute_query(query, (thread_id,))
        
        if result:
            row = result[0]
            return Conversation(
                id=row[0],
                thread_id=row[1],
                user_id=row[2],
                title=row[3],
                created_at=row[4],
                updated_at=row[5],
                last_message_at=row[6],
                message_count=row[7],
                is_archived=bool(row[8]),
                is_favorite=bool(row[9])
            )
        return None

    async def get_conversation_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Get a conversation by its unique ID."""
        query = """
        SELECT id, thread_id, user_id, title, created_at, updated_at,
               last_message_at, message_count, is_archived, is_favorite
        FROM conversations
        WHERE id = ?
        """
        
        result = await db_service.execute_query(query, (conversation_id,))
        
        if result:
            row = result[0]
            return Conversation(
                id=row[0],
                thread_id=row[1],
                user_id=row[2],
                title=row[3],
                created_at=row[4],
                updated_at=row[5],
                last_message_at=row[6],
                message_count=row[7],
                is_archived=bool(row[8]),
                is_favorite=bool(row[9])
            )
        return None

    async def get_user_conversations(
        self, 
        user_id: int, 
        include_archived: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """Get all conversations for a user, ordered by last message time."""
        archived_filter = "" if include_archived else "AND is_archived = FALSE"
        
        query = f"""
        SELECT id, thread_id, user_id, title, created_at, updated_at,
               last_message_at, message_count, is_archived, is_favorite
        FROM conversations
        WHERE user_id = ? {archived_filter}
        ORDER BY last_message_at DESC, updated_at DESC
        LIMIT ? OFFSET ?
        """
        
        result = await db_service.execute_query(query, (user_id, limit, offset))
        
        conversations = []
        for row in result:
            conversations.append(Conversation(
                id=row[0],
                thread_id=row[1],
                user_id=row[2],
                title=row[3],
                created_at=row[4],
                updated_at=row[5],
                last_message_at=row[6],
                message_count=row[7],
                is_archived=bool(row[8]),
                is_favorite=bool(row[9])
            ))
        
        return conversations

    async def update_conversation_activity(self, thread_id: str) -> None:
        """Update conversation's last message time and increment message count."""
        now = datetime.now().isoformat()
        
        query = """
        UPDATE conversations 
        SET last_message_at = ?, 
            message_count = message_count + 1,
            updated_at = ?
        WHERE thread_id = ?
        """
        
        await db_service.execute_query(query, (now, now, thread_id))
        
        # Auto-generate title after 3 messages if title is still default
        conversation = await self.get_conversation_by_thread_id(thread_id)
        if (conversation and 
            conversation.message_count >= 3 and 
            (not conversation.title or conversation.title in ["New Chat", f"Chat {datetime.now().strftime('%m/%d %H:%M')}"])):
            
            try:
                # Import here to avoid circular imports
                from app.services.llm import llm_service
                
                # For now, use a simple title generation
                # In a full implementation, you'd get the actual conversation history
                sample_history = ["User: Hello", "Assistant: Hi there!", "User: I need help"]
                new_title = await llm_service.generate_conversation_title(sample_history)
                await self.update_conversation_title(thread_id, new_title)
                print(f"🏷️ Auto-generated title for conversation {thread_id}: {new_title}")
            except Exception as e:
                print(f"⚠️ Failed to auto-generate title for {thread_id}: {e}")

    async def update_conversation_title(self, thread_id: str, title: str) -> bool:
        """Update conversation title."""
        now = datetime.now().isoformat()
        
        query = """
        UPDATE conversations 
        SET title = ?, updated_at = ?
        WHERE thread_id = ?
        """
        
        await db_service.execute_query(query, (title, now, thread_id))
        return True

    async def archive_conversation(self, thread_id: str, archived: bool = True) -> bool:
        """Archive or unarchive a conversation."""
        now = datetime.now().isoformat()
        
        query = """
        UPDATE conversations 
        SET is_archived = ?, updated_at = ?
        WHERE thread_id = ?
        """
        
        await db_service.execute_query(query, (archived, now, thread_id))
        return True

    async def favorite_conversation(self, thread_id: str, favorite: bool = True) -> bool:
        """Mark or unmark a conversation as favorite."""
        now = datetime.now().isoformat()
        
        query = """
        UPDATE conversations 
        SET is_favorite = ?, updated_at = ?
        WHERE thread_id = ?
        """
        
        await db_service.execute_query(query, (favorite, now, thread_id))
        return True

    async def delete_conversation(self, thread_id: str) -> bool:
        """Delete a conversation permanently."""
        query = "DELETE FROM conversations WHERE thread_id = ?"
        await db_service.execute_query(query, (thread_id,))
        return True

    async def get_or_create_conversation(
        self, 
        thread_id: str, 
        user_id: Optional[int] = None
    ) -> Conversation:
        """Get existing conversation or create new one if it doesn't exist."""
        conversation = await self.get_conversation_by_thread_id(thread_id)
        
        if conversation:
            return conversation
        
        # Create new conversation with a default title
        title = "New Chat" if not user_id else f"Chat {datetime.now().strftime('%m/%d %H:%M')}"
        return await self.create_conversation(thread_id, user_id, title)

    async def search_conversations(
        self, 
        user_id: int, 
        search_term: str,
        limit: int = 20
    ) -> List[Conversation]:
        """Search conversations by title."""
        query = """
        SELECT id, thread_id, user_id, title, created_at, updated_at,
               last_message_at, message_count, is_archived, is_favorite
        FROM conversations
        WHERE user_id = ? AND title LIKE ?
        ORDER BY last_message_at DESC
        LIMIT ?
        """
        
        search_pattern = f"%{search_term}%"
        result = await db_service.execute_query(query, (user_id, search_pattern, limit))
        
        conversations = []
        for row in result:
            conversations.append(Conversation(
                id=row[0],
                thread_id=row[1],
                user_id=row[2],
                title=row[3],
                created_at=row[4],
                updated_at=row[5],
                last_message_at=row[6],
                message_count=row[7],
                is_archived=bool(row[8]),
                is_favorite=bool(row[9])
            ))
        
        return conversations


# Create a singleton instance
conversation_service = ConversationService()
