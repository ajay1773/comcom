"""Resilience service for handling external calls with retry logic and circuit breakers."""
import asyncio
import time
import logging
from typing import Any, Callable, Optional
from functools import wraps
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class CircuitBreakerState:
    """State of a circuit breaker."""
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

class ResilienceService:
    """Service for handling external calls with resilience patterns."""

    def __init__(self):
        self.circuit_breakers: dict[str, CircuitBreakerState] = {}
        self.failure_threshold = 5  # Number of failures before opening circuit
        self.recovery_timeout = 60  # Seconds to wait before trying half-open
        self.timeout_duration = 30  # Default timeout for external calls

    def circuit_breaker(self, service_name: str):
        """Decorator for circuit breaker pattern."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                state = self.circuit_breakers.get(service_name, CircuitBreakerState())

                # Check if circuit is open
                if state.state == "OPEN":
                    if self._should_attempt_reset(state):
                        state.state = "HALF_OPEN"
                        logger.info(f"Circuit breaker for {service_name} moved to HALF_OPEN")
                    else:
                        raise CircuitBreakerOpenError(f"Circuit breaker is OPEN for {service_name}")

                try:
                    # Execute the function
                    result = await func(*args, **kwargs)

                    # Success - reset failure count and close circuit
                    if state.state == "HALF_OPEN":
                        state.failure_count = 0
                        state.state = "CLOSED"
                        logger.info(f"Circuit breaker for {service_name} reset to CLOSED")

                    return result

                except Exception as e:
                    # Handle failure
                    state.failure_count += 1
                    state.last_failure_time = datetime.now()

                    if state.failure_count >= self.failure_threshold:
                        state.state = "OPEN"
                        logger.warning(f"Circuit breaker for {service_name} opened after {state.failure_count} failures")

                    self.circuit_breakers[service_name] = state
                    raise e

            return wrapper
        return decorator

    def _should_attempt_reset(self, state: CircuitBreakerState) -> bool:
        """Check if enough time has passed to attempt resetting the circuit."""
        if not state.last_failure_time:
            return True

        time_since_failure = datetime.now() - state.last_failure_time
        return time_since_failure.total_seconds() >= self.recovery_timeout

    async def retry_with_backoff(
        self,
        func: Callable,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        *args,
        **kwargs
    ) -> Any:
        """Execute a function with exponential backoff retry logic."""
        last_exception = None

        for attempt in range(max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt == max_attempts - 1:
                    # Last attempt failed
                    logger.error(f"Function failed after {max_attempts} attempts: {str(e)}")
                    raise e

                # Calculate delay with exponential backoff
                delay = min(base_delay * (backoff_factor ** attempt), max_delay)

                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
                await asyncio.sleep(delay)

        # This should never be reached, but just in case
        raise last_exception

    async def call_with_timeout(
        self,
        func: Callable,
        timeout: Optional[float] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute a function with a timeout."""
        timeout_duration = timeout or self.timeout_duration

        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_duration)
        except asyncio.TimeoutError:
            logger.error(f"Function call timed out after {timeout_duration}s")
            raise TimeoutError(f"Operation timed out after {timeout_duration} seconds")

    async def resilient_call(
        self,
        func: Callable,
        service_name: str,
        max_attempts: int = 3,
        timeout: Optional[float] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute a function with full resilience: circuit breaker + retry + timeout."""
        @self.circuit_breaker(service_name)
        async def circuit_breaker_wrapper():
            return await self.retry_with_backoff(
                func,
                max_attempts=max_attempts,
                *args,
                **kwargs
            )

        return await self.call_with_timeout(
            circuit_breaker_wrapper,
            timeout=timeout
        )

    def get_circuit_breaker_status(self, service_name: str) -> dict:
        """Get the status of a circuit breaker."""
        state = self.circuit_breakers.get(service_name, CircuitBreakerState())
        return {
            "service_name": service_name,
            "state": state.state,
            "failure_count": state.failure_count,
            "last_failure_time": state.last_failure_time.isoformat() if state.last_failure_time else None
        }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Global instance
resilience_service = ResilienceService()


# Convenience functions for common use cases
async def call_external_api(url: str, **kwargs) -> Any:
    """Example function for calling external APIs with resilience."""
    import aiohttp

    async def _call():
        async with aiohttp.ClientSession() as session:
            async with session.get(url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()

    return await resilience_service.resilient_call(
        _call,
        service_name=f"api_call_{url}",
        max_attempts=3
    )


async def call_database_operation(operation_func: Callable, *args, **kwargs) -> Any:
    """Example function for database operations with resilience."""
    return await resilience_service.resilient_call(
        operation_func,
        service_name="database_operation",
        max_attempts=2,  # Fewer retries for DB operations
        *args,
        **kwargs
    )
