"""Monitoring service for structured logging and metrics."""
import logging
import time
import json
from typing import Any, Dict, Optional
from datetime import datetime
from functools import wraps
from contextlib import asynccontextmanager
import asyncio
from collections import defaultdict, deque

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class StructuredLogger:
    """Logger that outputs structured JSON logs."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _log_structured(self, level: str, message: str, **kwargs):
        """Log a structured message with additional context."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "service": "langgraph_app",
            **kwargs
        }

        log_method = getattr(self.logger, level.lower())
        log_method(json.dumps(log_data))

    def info(self, message: str, **kwargs):
        self._log_structured("INFO", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log_structured("ERROR", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log_structured("WARNING", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log_structured("DEBUG", message, **kwargs)


class MetricsCollector:
    """Simple metrics collector for monitoring."""

    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        self.timers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.gauges: Dict[str, float] = {}

    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter metric."""
        self.counters[name] += value

    def record_timer(self, name: str, duration: float):
        """Record a timer metric."""
        self.timers[name].append(duration)

    def set_gauge(self, name: str, value: float):
        """Set a gauge metric."""
        self.gauges[name] = value

    def get_counter(self, name: str) -> int:
        """Get counter value."""
        return self.counters[name]

    def get_timer_stats(self, name: str) -> Dict[str, float]:
        """Get timer statistics."""
        if name not in self.timers:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}

        durations = list(self.timers[name])
        return {
            "count": len(durations),
            "avg": sum(durations) / len(durations) if durations else 0,
            "min": min(durations) if durations else 0,
            "max": max(durations) if durations else 0
        }

    def get_gauge(self, name: str) -> float:
        """Get gauge value."""
        return self.gauges.get(name, 0)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timers": {name: self.get_timer_stats(name) for name in self.timers}
        }


class MonitoringService:
    """Main monitoring service."""

    def __init__(self):
        self.logger = StructuredLogger("monitoring")
        self.metrics = MetricsCollector()

    def log_workflow_start(self, workflow_name: str, thread_id: str, user_message: str):
        """Log workflow start event."""
        self.logger.info(
            f"Workflow {workflow_name} started",
            event_type="workflow_start",
            workflow_name=workflow_name,
            thread_id=thread_id,
            user_message_length=len(user_message)
        )
        self.metrics.increment_counter(f"workflow_{workflow_name}_started")

    def log_workflow_end(self, workflow_name: str, thread_id: str, duration: float, success: bool):
        """Log workflow end event."""
        self.logger.info(
            f"Workflow {workflow_name} completed",
            event_type="workflow_end",
            workflow_name=workflow_name,
            thread_id=thread_id,
            duration=duration,
            success=success
        )
        self.metrics.record_timer(f"workflow_{workflow_name}_duration", duration)
        self.metrics.increment_counter(f"workflow_{workflow_name}_completed")
        if not success:
            self.metrics.increment_counter(f"workflow_{workflow_name}_failed")

    def log_node_execution(self, node_name: str, workflow_name: str, duration: float, success: bool):
        """Log node execution event."""
        self.logger.info(
            f"Node {node_name} executed",
            event_type="node_execution",
            node_name=node_name,
            workflow_name=workflow_name,
            duration=duration,
            success=success
        )
        self.metrics.record_timer(f"node_{node_name}_duration", duration)

    def log_error(self, error_type: str, workflow_name: str, thread_id: str, error_message: str):
        """Log error event."""
        self.logger.error(
            f"Error in {workflow_name}: {error_type}",
            event_type="error",
            error_type=error_type,
            workflow_name=workflow_name,
            thread_id=thread_id,
            error_message=error_message
        )
        self.metrics.increment_counter(f"error_{error_type}")

    def log_streaming_event(self, event_type: str, thread_id: str, data_size: int = 0):
        """Log streaming event."""
        # Reduce logging verbosity for high-frequency events
        if event_type not in ["llm_stream", "on_chat_model_stream"]:
            self.logger.debug(
                f"Streaming event: {event_type}",
                event_type="streaming",
                stream_event_type=event_type,
                thread_id=thread_id,
                data_size=data_size
            )
        self.metrics.increment_counter(f"streaming_{event_type}")

    @asynccontextmanager
    async def monitor_workflow(self, workflow_name: str, thread_id: str, user_message: str):
        """Context manager for monitoring workflow execution."""
        start_time = time.time()
        self.log_workflow_start(workflow_name, thread_id, user_message)

        try:
            yield
            success = True
        except Exception as e:
            success = False
            duration = time.time() - start_time
            self.log_workflow_end(workflow_name, thread_id, duration, success)
            self.log_error("workflow_exception", workflow_name, thread_id, str(e))
            raise
        else:
            duration = time.time() - start_time
            self.log_workflow_end(workflow_name, thread_id, duration, success)

    @asynccontextmanager
    async def monitor_node(self, node_name: str, workflow_name: str):
        """Context manager for monitoring node execution."""
        start_time = time.time()

        try:
            yield
            success = True
        except Exception as e:
            success = False
            duration = time.time() - start_time
            self.log_node_execution(node_name, workflow_name, duration, success)
            raise
        else:
            duration = time.time() - start_time
            self.log_node_execution(node_name, workflow_name, duration, success)

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the application."""
        metrics = self.metrics.get_all_metrics()

        # Simple health checks
        total_workflows = sum(metrics["counters"].get(f"workflow_{w}_started", 0)
                            for w in ["product_search", "place_order", "initiate_payment", "payment_status"])

        failed_workflows = sum(metrics["counters"].get(f"workflow_{w}_failed", 0)
                             for w in ["product_search", "place_order", "initiate_payment", "payment_status"])

        success_rate = (total_workflows - failed_workflows) / total_workflows if total_workflows > 0 else 1.0

        return {
            "status": "healthy" if success_rate > 0.95 else "degraded",
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "success_rate": success_rate,
            "total_workflows": total_workflows,
            "failed_workflows": failed_workflows
        }


# Global monitoring service instance
monitoring_service = MonitoringService()

# Convenience functions
def monitor_workflow(workflow_name: str, thread_id: str, user_message: str):
    """Decorator for monitoring workflow functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with monitoring_service.monitor_workflow(workflow_name, thread_id, user_message):
                return await func(*args, **kwargs)
        return wrapper
    return decorator

def monitor_node(node_name: str, workflow_name: str):
    """Decorator for monitoring node functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with monitoring_service.monitor_node(node_name, workflow_name):
                return await func(*args, **kwargs)
        return wrapper
    return decorator
