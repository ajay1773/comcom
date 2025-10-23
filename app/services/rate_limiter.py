"""Rate limiting and token usage tracking service."""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta, date
from app.services.db.db import db_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Exception raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: Optional[int] = None, limit_type: str = "requests"):
        self.message = message
        self.retry_after = retry_after  # Seconds until limit resets
        self.limit_type = limit_type  # "requests" or "tokens"
        super().__init__(self.message)


class RateLimiterService:
    """Service for handling rate limiting and token usage tracking."""

    def __init__(self):
        self.requests_per_hour = settings.RATE_LIMIT_REQUESTS_PER_HOUR
        self.window_hours = settings.RATE_LIMIT_WINDOW_HOURS
        self.daily_token_limit = settings.DAILY_TOKEN_LIMIT
        self.token_reset_hour = settings.TOKEN_LIMIT_RESET_HOUR

    async def check_rate_limit_for_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Check rate limit for logged-out users (IP-based).
        Returns dict with allowed status and remaining requests.
        Raises RateLimitError if limit exceeded.
        """
        now = datetime.now()
        window_start = now.replace(minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(hours=self.window_hours)

        # Clean up old rate limit records (older than 24 hours)
        await self._cleanup_old_rate_limits()

        # Get or create rate limit record for this IP in current window
        result = await db_service.execute_query(
            """
            SELECT id, request_count, window_end 
            FROM rate_limit_tracking 
            WHERE ip_address = ? AND window_start = ?
            """,
            (ip_address, window_start)
        )

        if result:
            # Existing record found
            record_id, request_count, stored_window_end = result[0]
            
            if request_count >= self.requests_per_hour:
                # Rate limit exceeded
                time_until_reset = (datetime.fromisoformat(stored_window_end) - now).total_seconds()
                raise RateLimitError(
                    message=f"Rate limit exceeded. Maximum {self.requests_per_hour} requests per hour. Please sign in for higher limits.",
                    retry_after=int(time_until_reset),
                    limit_type="requests"
                )
            
            # Increment request count
            await db_service.execute_query(
                """
                UPDATE rate_limit_tracking 
                SET request_count = request_count + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (record_id,)
            )
            
            remaining_requests = self.requests_per_hour - (request_count + 1)
            
        else:
            # Create new record
            await db_service.execute_query(
                """
                INSERT INTO rate_limit_tracking (ip_address, request_count, window_start, window_end)
                VALUES (?, 1, ?, ?)
                """,
                (ip_address, window_start, window_end)
            )
            
            remaining_requests = self.requests_per_hour - 1

        return {
            "allowed": True,
            "remaining_requests": remaining_requests,
            "limit": self.requests_per_hour,
            "reset_time": window_end.isoformat()
        }

    async def check_token_limit_for_user(self, user_id: int) -> Dict[str, Any]:
        """
        Check token usage limit for logged-in users.
        Returns dict with allowed status and remaining tokens.
        Does NOT raise exception - just returns status.
        """
        today = date.today()
        
        # Get or create token usage record for today
        result = await db_service.execute_query(
            """
            SELECT id, tokens_used, daily_limit, reset_date 
            FROM user_token_usage 
            WHERE user_id = ? AND reset_date = ?
            """,
            (user_id, today)
        )

        if result:
            # Existing record found
            record_id, tokens_used, daily_limit, reset_date = result[0]
            
            remaining_tokens = daily_limit - tokens_used
            is_allowed = tokens_used < daily_limit
            
            return {
                "allowed": is_allowed,
                "tokens_used": tokens_used,
                "remaining_tokens": remaining_tokens,
                "daily_limit": daily_limit,
                "reset_date": reset_date
            }
        else:
            # Create new record for today
            await db_service.execute_query(
                """
                INSERT INTO user_token_usage (user_id, tokens_used, daily_limit, reset_date)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, 0, self.daily_token_limit, today)
            )
            
            return {
                "allowed": True,
                "tokens_used": 0,
                "remaining_tokens": self.daily_token_limit,
                "daily_limit": self.daily_token_limit,
                "reset_date": today.isoformat()
            }

    async def record_token_usage(self, user_id: int, tokens_used: int) -> Dict[str, Any]:
        """
        Record token usage for a logged-in user.
        Updates the daily usage and returns current status.
        """
        today = date.today()
        
        # Get or create record for today
        await self.check_token_limit_for_user(user_id)  # Ensures record exists
        
        # Update token usage
        result = await db_service.execute_query(
            """
            UPDATE user_token_usage 
            SET tokens_used = tokens_used + ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND reset_date = ?
            RETURNING tokens_used, daily_limit
            """,
            (tokens_used, user_id, today)
        )

        if result:
            new_tokens_used, daily_limit = result[0]
            remaining_tokens = daily_limit - new_tokens_used
            
            logger.info(f"User {user_id} used {tokens_used} tokens. Total today: {new_tokens_used}/{daily_limit}")
            
            return {
                "tokens_used": new_tokens_used,
                "remaining_tokens": remaining_tokens,
                "daily_limit": daily_limit,
                "tokens_added": tokens_used
            }
        
        return {
            "tokens_used": 0,
            "remaining_tokens": self.daily_token_limit,
            "daily_limit": self.daily_token_limit,
            "tokens_added": 0
        }

    async def get_user_token_status(self, user_id: int) -> Dict[str, Any]:
        """
        Get current token usage status for a user without checking limits.
        """
        return await self.check_token_limit_for_user(user_id)

    async def get_rate_limit_status_for_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Get current rate limit status for an IP address WITHOUT incrementing the counter.
        This is used for status checks only.
        """
        now = datetime.now()
        window_start = now.replace(minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(hours=self.window_hours)

        # Get rate limit record for this IP in current window (READ ONLY - no increment)
        result = await db_service.execute_query(
            """
            SELECT id, request_count, window_end 
            FROM rate_limit_tracking 
            WHERE ip_address = ? AND window_start = ?
            """,
            (ip_address, window_start)
        )

        if result:
            # Existing record found
            record_id, request_count, stored_window_end = result[0]
            
            remaining_requests = max(0, self.requests_per_hour - request_count)
            is_limited = request_count >= self.requests_per_hour
            
            if is_limited:
                time_until_reset = (datetime.fromisoformat(stored_window_end) - now).total_seconds()
                return {
                    "allowed": False,
                    "remaining_requests": 0,
                    "limit": self.requests_per_hour,
                    "reset_time": window_end.isoformat(),
                    "limit_exceeded": True,
                    "retry_after": int(time_until_reset)
                }
            
            return {
                "allowed": True,
                "remaining_requests": remaining_requests,
                "limit": self.requests_per_hour,
                "reset_time": window_end.isoformat(),
                "limit_exceeded": False
            }
        else:
            # No record exists yet - user hasn't made any requests in this window
            return {
                "allowed": True,
                "remaining_requests": self.requests_per_hour,
                "limit": self.requests_per_hour,
                "reset_time": window_end.isoformat(),
                "limit_exceeded": False
            }

    async def reset_user_daily_tokens(self, user_id: int) -> bool:
        """
        Manually reset user's daily token usage (admin function).
        """
        today = date.today()
        
        await db_service.execute_query(
            """
            UPDATE user_token_usage 
            SET tokens_used = 0, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND reset_date = ?
            """,
            (user_id, today)
        )
        
        logger.info(f"Reset daily token usage for user {user_id}")
        return True

    async def update_user_token_limit(self, user_id: int, new_limit: int) -> bool:
        """
        Update daily token limit for a specific user (admin function).
        """
        today = date.today()
        
        # Ensure record exists
        await self.check_token_limit_for_user(user_id)
        
        await db_service.execute_query(
            """
            UPDATE user_token_usage 
            SET daily_limit = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND reset_date = ?
            """,
            (new_limit, user_id, today)
        )
        
        logger.info(f"Updated daily token limit for user {user_id} to {new_limit}")
        return True

    async def _cleanup_old_rate_limits(self) -> None:
        """Clean up rate limit records older than 24 hours."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        await db_service.execute_query(
            "DELETE FROM rate_limit_tracking WHERE window_end < ?",
            (cutoff_time,)
        )

    async def cleanup_old_token_records(self) -> None:
        """Clean up token usage records older than 30 days."""
        cutoff_date = date.today() - timedelta(days=30)
        
        await db_service.execute_query(
            "DELETE FROM user_token_usage WHERE reset_date < ?",
            (cutoff_date,)
        )
        
        logger.info(f"Cleaned up token usage records older than {cutoff_date}")


# Singleton instance
rate_limiter_service = RateLimiterService()

