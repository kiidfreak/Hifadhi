"""
Complete Phoenix (Arize) observability setup for Hifadhi
Provides distributed tracing, prompt monitoring, and performance analytics
"""

import os
import logging
from functools import wraps
import time
from typing import Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================
# PHOENIX CONFIGURATION
# ============================================

PHOENIX_COLLECTOR_ENDPOINT = os.getenv(
    "PHOENIX_COLLECTOR_ENDPOINT", 
    "http://127.0.0.1:6006/v1/traces"
)

PROJECT_NAME = "hifadhi-multi-agent"

# Try to import Phoenix components
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.trace.status import Status, StatusCode
    from opentelemetry.trace import get_current_span
    
    # Initialize Phoenix tracer
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)
    
    # Add OTLP exporter
    otlp_exporter = OTLPSpanExporter(endpoint=PHOENIX_COLLECTOR_ENDPOINT)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    tracer = tracer_provider.get_tracer(__name__)
    PHOENIX_AVAILABLE = True
    logger.info(f"✅ Phoenix tracer initialized: {PHOENIX_COLLECTOR_ENDPOINT}")
    
except Exception as e:
    PHOENIX_AVAILABLE = False
    logger.warning(f"⚠️ Phoenix not available: {e}")
    # Create dummy implementations for when Phoenix is not available
    class DummySpan:
        def set_attribute(self, key, value): pass
        def record_exception(self, exc): pass
        def set_status(self, status): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
    
    class DummyTracer:
        def start_as_current_span(self, name): return DummySpan()
        def start_span(self, name): return DummySpan()
    
    tracer = DummyTracer()
    def get_current_span(): return DummySpan()
    class Status:
        def __init__(self, code, message=""): pass
    class StatusCode:
        OK = "ok"
        ERROR = "error"


# ============================================
# AGENT TRACING DECORATOR
# ============================================

def trace_agent(func: Callable) -> Callable:
    """
    Decorator to wrap agent functions with Phoenix spans
    
    Captures:
    - Agent name and type
    - Execution duration
    - Input/output state
    - User context (candidate ID, job ID, etc.)
    - Errors and exceptions
    """
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract state from args
        state = args[0] if args else {}
        agent_name = func.__name__
        
        # Start Phoenix span
        with tracer.start_as_current_span(agent_name) as span:
            
            # Set span attributes (metadata)
            span.set_attribute("agent.name", agent_name)
            span.set_attribute("agent.type", agent_name.replace("_agent", "").replace("_node", ""))
            span.set_attribute("agent.version", "1.0.0")
            
            # User context
            span.set_attribute("user.query", str(state.get("user_input", ""))[:200])
            span.set_attribute("user.candidate_id", str(state.get("candidate_id", "unknown")))
            span.set_attribute("user.job_id", str(state.get("job_id", "unknown")))
            
            # Conversation context
            span.set_attribute("conversation.iteration", state.get("n_iteration", 0))
            span.set_attribute("conversation.session_id", str(state.get("session_id", "unknown")))
            
            # Task context
            span.set_attribute("task.description", str(state.get("task", "none"))[:200])
            span.set_attribute("task.next_agent", str(state.get("next_agent", "none")))
            
            # Timestamp
            span.set_attribute("timestamp", datetime.now().isoformat())
            
            # Record start time
            start_time = time.time()
            
            try:
                # Execute agent function
                result = func(*args, **kwargs)
                
                # Record success metrics
                duration = time.time() - start_time
                span.set_attribute("execution.duration_seconds", round(duration, 3))
                span.set_attribute("execution.status", "success")
                
                # Record output metadata
                if isinstance(result, dict):
                    span.set_attribute("output.keys", ",".join(str(k) for k in result.keys()))
                    
                    if "final_answer" in result:
                        span.set_attribute("output.final_answer_length", len(str(result["final_answer"])))
                    
                    if "messages" in result:
                        span.set_attribute("output.message_count", len(result["messages"]))
                
                if PHOENIX_AVAILABLE:
                    span.set_status(Status(StatusCode.OK))
                
                logger.debug(f"✅ {agent_name} completed in {duration:.3f}s")
                
                return result
            
            except Exception as e:
                # Record failure metrics
                duration = time.time() - start_time
                span.set_attribute("execution.duration_seconds", round(duration, 3))
                span.set_attribute("execution.status", "error")
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e)[:500])
                
                # Record exception in span
                span.record_exception(e)
                if PHOENIX_AVAILABLE:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                
                logger.error(f"❌ {agent_name} failed after {duration:.3f}s: {e}")
                
                # Re-raise exception
                raise
    
    return wrapper


# ============================================
# TOOL CALL TRACING
# ============================================

def trace_tool_call(tool_name: str, **params):
    """
    Trace individual tool executions
    
    Args:
        tool_name: Name of the tool being called
        **params: Tool parameters to log
    
    Returns:
        Context manager for tool span
    """
    
    span = tracer.start_span(f"tool.{tool_name}")
    
    # Set tool metadata
    span.set_attribute("tool.name", tool_name)
    span.set_attribute("tool.type", "database" if "get_" in tool_name else "action")
    
    # Log parameters (sanitize sensitive data)
    for key, value in params.items():
        if key not in ["password", "api_key", "token"]:
            span.set_attribute(f"tool.param.{key}", str(value)[:100])
    
    span.set_attribute("tool.timestamp", datetime.now().isoformat())
    
    return span


# ============================================
# CUSTOM METRICS
# ============================================

class MetricsCollector:
    """Collect custom metrics for Hifadhi operations"""
    
    def __init__(self):
        self.metrics = {
            "total_conversations": 0,
            "total_agent_calls": 0,
            "total_tool_calls": 0,
            "total_llm_calls": 0,
            "total_escalations": 0,
            "total_errors": 0,
            "average_conversation_duration": 0.0,
            "agent_call_counts": {},
            "tool_call_counts": {}
        }
    
    def record_conversation(self, duration: float, success: bool, escalated: bool):
        """Record conversation-level metrics"""
        self.metrics["total_conversations"] += 1
        
        if not success:
            self.metrics["total_errors"] += 1
        
        if escalated:
            self.metrics["total_escalations"] += 1
        
        # Update average duration
        total = self.metrics["total_conversations"]
        current_avg = self.metrics["average_conversation_duration"]
        self.metrics["average_conversation_duration"] = (
            (current_avg * (total - 1) + duration) / total
        )
    
    def record_agent_call(self, agent_name: str):
        """Record agent invocation"""
        self.metrics["total_agent_calls"] += 1
        
        if agent_name not in self.metrics["agent_call_counts"]:
            self.metrics["agent_call_counts"][agent_name] = 0
        
        self.metrics["agent_call_counts"][agent_name] += 1
    
    def record_tool_call(self, tool_name: str):
        """Record tool invocation"""
        self.metrics["total_tool_calls"] += 1
        
        if tool_name not in self.metrics["tool_call_counts"]:
            self.metrics["tool_call_counts"][tool_name] = 0
        
        self.metrics["tool_call_counts"][tool_name] += 1
    
    def get_metrics(self) -> dict:
        """Get current metrics snapshot"""
        return self.metrics.copy()


# Global metrics collector
metrics_collector = MetricsCollector()


# ============================================
# PHOENIX DASHBOARD HELPERS
# ============================================

def get_phoenix_dashboard_url() -> str:
    """Get URL to Phoenix dashboard"""
    base_url = PHOENIX_COLLECTOR_ENDPOINT.replace("/v1/traces", "")
    return f"{base_url}/projects/{PROJECT_NAME}"


def print_observability_info():
    """Print observability setup information"""
    print("\n" + "="*70)
    print("🔭 PHOENIX OBSERVABILITY")
    print("="*70)
    print(f"\nProject: {PROJECT_NAME}")
    print(f"Endpoint: {PHOENIX_COLLECTOR_ENDPOINT}")
    print(f"Dashboard: {get_phoenix_dashboard_url()}")
    print("\nTo view traces:")
    print("  1. Run: docker-compose up phoenix")
    print("  2. Open: http://localhost:6006")
    print("="*70 + "\n")


def initialize_observability():
    """Initialize all observability components"""
    try:
        if PHOENIX_AVAILABLE:
            logger.info("Initializing Phoenix observability...")
            print_observability_info()
            logger.info("✅ Observability initialized successfully")
        else:
            logger.info("⚠️ Running without Phoenix observability")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize observability: {e}")
        return False
