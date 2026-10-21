from pydantic import BaseModel
from typing import Dict, Any, Optional

class DataPayload(BaseModel):
# Standard payload contract for writing data
    key: str
    value: Any
    is_sensitive: bool = False

class SystemHealth(BaseModel):
# Status report model returned by worker health check endpoints
    status: str
    node_id: str
    active_connections: int = 0
    stored_keys_count: int = 0

class DistributedResponse(BaseModel):
# Standard unified JSON response structure across all nodes
    status: str
    node_id: str
    message: str
    data: Optional[Dict[str, Any]] = None
    trace_id: str