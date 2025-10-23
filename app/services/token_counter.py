"""Token counting service for tracking LLM usage."""

from typing import Optional, Dict, Any
import tiktoken
import logging

logger = logging.getLogger(__name__)


class TokenCounterService:
    """Service for counting tokens in LLM interactions."""

    def __init__(self):
        # Use cl100k_base encoding (used by GPT-3.5/4 and similar models)
        # This is a good approximation for most modern LLMs
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Failed to load tiktoken encoding: {e}. Using simple estimation.")
            self.encoding = None

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0

        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception as e:
                logger.warning(f"Error encoding text: {e}. Using fallback estimation.")
                return self._estimate_tokens_simple(text)
        else:
            return self._estimate_tokens_simple(text)

    def _estimate_tokens_simple(self, text: str) -> int:
        """
        Simple token estimation based on character count.
        Rule of thumb: ~4 characters per token for English text.
        
        Args:
            text: The text to estimate tokens for
            
        Returns:
            Estimated number of tokens
        """
        return max(1, len(text) // 4)

    def count_messages_tokens(self, messages: list) -> int:
        """
        Count tokens in a list of messages (conversation format).
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            
        Returns:
            Total number of tokens including message formatting overhead
        """
        total_tokens = 0
        
        for message in messages:
            # Count content tokens
            content = message.get('content', '')
            if isinstance(content, str):
                total_tokens += self.count_tokens(content)
            
            # Add overhead for message structure (role, formatting, etc.)
            # Based on OpenAI's token counting guidelines
            total_tokens += 4  # Role and message formatting overhead
        
        # Add overhead for message list formatting
        total_tokens += 2
        
        return total_tokens

    def estimate_completion_tokens(self, prompt: str, completion: str) -> Dict[str, int]:
        """
        Estimate tokens for a prompt-completion pair.
        
        Args:
            prompt: The input prompt
            completion: The generated completion
            
        Returns:
            Dict with prompt_tokens, completion_tokens, and total_tokens
        """
        prompt_tokens = self.count_tokens(prompt)
        completion_tokens = self.count_tokens(completion)
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }

    def estimate_stream_tokens(self, accumulated_text: str) -> int:
        """
        Estimate tokens for streaming response (as it accumulates).
        
        Args:
            accumulated_text: The accumulated streaming text so far
            
        Returns:
            Number of tokens
        """
        return self.count_tokens(accumulated_text)


# Singleton instance
token_counter_service = TokenCounterService()

