import logging
import uuid
from contextvars import ContextVar

# Context Variable to store X-Trace-ID per request lifecycle
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="NO_TRACE_ID")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Trace-ID: %(trace_id)s] %(message)s"
)

class TraceLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f"{msg}", {**kwargs, "extra": {"trace_id": trace_id_var.get()}}

def get_logger(name: str):
    logger = logging.getLogger(name)
    return TraceLoggerAdapter(logger, {})

def generate_trace_id() -> str:
    return str(uuid.uuid4())[:8]