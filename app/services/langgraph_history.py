"""
LangGraph History Service

This service provides functionality to retrieve conversation history from LangGraph's
checkpointer database. It connects to the same SQLite database that LangGraph uses
to store conversation states and extracts the conversation_history field.
"""

import aiosqlite
import msgpack
from typing import List, Dict, Any
from app.core.config import Settings

settings = Settings()


class LangGraphHistoryService:
    """Service for retrieving conversation history from LangGraph checkpointer."""
    
    def __init__(self):
        self.db_path = settings.DATABASE_URL
    
    async def get_conversation_history(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history from LangGraph checkpointer.
        
        Args:
            thread_id: The LangGraph thread identifier
            
        Returns:
            List of message dictionaries with role, content, and timestamp
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                # Query the checkpoints table for the latest state of this thread
                cursor = await conn.execute("""
                    SELECT checkpoint 
                    FROM checkpoints 
                    WHERE thread_id = ? 
                    ORDER BY checkpoint_id DESC 
                    LIMIT 1
                """, (thread_id,))
                
                row = await cursor.fetchone()
                
                if not row:
                    print(f"📚 No checkpoint found for thread {thread_id}")
                    return []
                
                # Parse the checkpoint data (stored as MessagePack)
                checkpoint_data = msgpack.unpackb(row[0], raw=False)
                
                # Extract conversation_history from the channel data
                # LangGraph stores state in channels, we need to find the conversation_history
                conversation_history = []
                
                if 'channel_values' in checkpoint_data:
                    channel_values = checkpoint_data['channel_values']
                    if 'conversation_history' in channel_values:
                        conversation_history = channel_values['conversation_history']
                
                # Parse the conversation history strings into structured messages
                messages = self._parse_conversation_history(conversation_history)
                
                print(f"📚 Retrieved {len(messages)} messages from LangGraph for thread {thread_id}")
                return messages
                
        except Exception as e:
            print(f"❌ Error retrieving conversation history for thread {thread_id}: {e}")
            return []
    
    def _parse_conversation_history(self, conversation_history: List[str]) -> List[Dict[str, Any]]:
        """
        Parse conversation history strings into structured message objects.
        
        Args:
            conversation_history: List of strings like ["User: Hello", "Assistant: Hi there"]
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        for entry in conversation_history:
            if not isinstance(entry, str):
                continue
                
            # Parse "User: message" or "Assistant: message" format
            if entry.startswith("User: "):
                messages.append({
                    "role": "user",
                    "content": entry[6:],  # Remove "User: " prefix
                    "timestamp": None  # We don't have timestamps in the history strings
                })
            elif entry.startswith("Assistant: "):
                # Parse assistant messages that may contain widget JSON
                assistant_data = self._parse_assistant_entry(entry)
                messages.append(assistant_data)
            elif entry.startswith("Workflow: "):
                # Skip workflow entries for now, or convert them to assistant messages
                messages.append({
                    "role": "assistant",
                    "content": f"[System] {entry}",
                    "timestamp": None
                })
        
        return messages
    
    def _parse_assistant_entry(self, entry: str) -> Dict[str, Any]:
        """
        Parse an assistant entry that may contain widget JSON.
        
        Format: "Assistant: message text | Widget: {json_data}"
        
        Args:
            entry: The assistant entry string
            
        Returns:
            Dictionary with role, content, and optional widget_json
        """
        try:
            # Remove "Assistant: " prefix
            assistant_content = entry[11:]  # Remove "Assistant: "
            
            # Check if there's widget JSON
            if " | Widget: " in assistant_content:
                # Split into text and widget parts
                text_part, widget_part = assistant_content.split(" | Widget: ", 1)
                
                # Parse the JSON
                import json
                try:
                    widget_json = json.loads(widget_part)
                    return {
                        "role": "assistant",
                        "content": text_part.strip(),
                        "timestamp": None,
                        "widget_json": widget_json
                    }
                except json.JSONDecodeError as e:
                    print(f"⚠️ Error parsing widget JSON: {e}")
                    # Fallback to text only
                    return {
                        "role": "assistant",
                        "content": assistant_content,
                        "timestamp": None
                    }
            else:
                # No widget JSON, just text
                return {
                    "role": "assistant",
                    "content": assistant_content,
                    "timestamp": None
                }
                
        except Exception as e:
            print(f"⚠️ Error parsing assistant entry: {e}")
            # Fallback to basic assistant message
            return {
                "role": "assistant",
                "content": entry[11:] if entry.startswith("Assistant: ") else entry,
                "timestamp": None
            }
    
    async def save_message_to_history(self, thread_id: str, role: str, content: str) -> bool:
        """
        Add a message to the conversation history in LangGraph state.
        
        Note: This is a complex operation that requires updating the LangGraph state.
        For now, we'll rely on LangGraph's natural flow to update the history.
        
        Args:
            thread_id: The thread to update
            role: "user" or "assistant"
            content: The message content
            
        Returns:
            bool: Success status
        """
        # TODO: Implement if needed - this is complex because it requires
        # updating the LangGraph state properly. For now, LangGraph handles
        # this automatically during conversation flow.
        print(f"📝 Message saving to LangGraph state is handled automatically during conversation flow")
        return True
    
    async def get_thread_ids(self, limit: int = 100) -> List[str]:
        """
        Get all available thread IDs from the checkpointer.
        
        Args:
            limit: Maximum number of thread IDs to return
            
        Returns:
            List of thread ID strings
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute("""
                    SELECT DISTINCT thread_id 
                    FROM checkpoints 
                    ORDER BY checkpoint_id DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = await cursor.fetchall()
                thread_ids = [row[0] for row in rows]
                
                print(f"📚 Found {len(thread_ids)} thread IDs in LangGraph checkpointer")
                return thread_ids
                
        except Exception as e:
            print(f"❌ Error retrieving thread IDs: {e}")
            return []
    
    async def thread_exists(self, thread_id: str) -> bool:
        """
        Check if a thread exists in the checkpointer.
        
        Args:
            thread_id: The thread ID to check
            
        Returns:
            bool: True if thread exists
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute("""
                    SELECT 1 FROM checkpoints WHERE thread_id = ? LIMIT 1
                """, (thread_id,))
                
                row = await cursor.fetchone()
                return row is not None
                
        except Exception as e:
            print(f"❌ Error checking thread existence: {e}")
            return False


# Global instance
langgraph_history_service = LangGraphHistoryService()
