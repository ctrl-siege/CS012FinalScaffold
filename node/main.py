import os
import asyncio
from fastapi import FastAPI, Header, HTTPException, Request
from common.models import DataPayload, SystemHealth, DistributedResponse
from common.logger import get_logger, trace_id_var

NODE_ID = os.getenv("NODE_ID", "Worker-Default")
PORT = int(os.getenv("PORT", "8001"))
IS_PRIVATE_NODE = os.getenv("IS_PRIVATE", "false").lower() == "true"

app = FastAPI(title=f"Worker Node {NODE_ID}")
logger = get_logger(NODE_ID)

local_store: dict[str, str] = {}

@app.middleware("http")
async def trace_and_security_middleware(request: Request, call_next):
    # 1. Trace ID Extraction
    trace_id = request.headers.get("X-Trace-ID", "NO_TRACE_ID")
    trace_id_var.set(trace_id)
    
    # 2. Cloud Deployment Model Simulation (Private Cloud / VPC Middleware Security Check)
    if IS_PRIVATE_NODE and request.url.path in ["/store", "/read"]:
        network_zone = request.headers.get("X-Network-Zone")
        if network_zone != "PRIVATE_VPC":
            logger.warning("Access denied: Private VPC Token missing.")
            raise HTTPException(status_code=403, detail="Forbidden: Node reachable only via Private Cloud VPC network.")

    logger.info(f"Processing request: {request.method} {request.url.path}")
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response

# Check status of all nodes
@app.get("/health", response_model=SystemHealth)
async def health_check():
    return SystemHealth(
        status="HEALTHY",
        node_id=NODE_ID,
        stored_keys_count=len(local_store)
    )

@app.post("/store", response_model=DistributedResponse)
async def store_data(payload: DataPayload, x_trace_id: str = Header(default="")):
    # Simulate low LAN latency for internal nodes vs WAN latency
    await asyncio.sleep(0.02)
    local_store[payload.key] = str(payload.value)
    logger.info(f"Stored key '{payload.key}' successfully.")
    
    return DistributedResponse(
        status="SUCCESS",
        node_id=NODE_ID,
        message=f"Key '{payload.key}' stored on node {NODE_ID}",
        data={"key": payload.key, "value": payload.value},
        trace_id=trace_id_var.get()
    )

@app.get("/read/{key}", response_model=DistributedResponse)
async def read_data(key: str, simulate_delay: float = 0.0):
    if simulate_delay > 0:
        logger.info(f"Simulating network latency delay of {simulate_delay}s...")
        await asyncio.sleep(simulate_delay)
        
    if key not in local_store:
        raise HTTPException(status_code=404, detail="Key not found on this node")
        
    return DistributedResponse(
        status="SUCCESS",
        node_id=NODE_ID,
        message="Data retrieved",
        data={"key": key, "value": local_store[key]},
        trace_id=trace_id_var.get()
    )

@app.post("/compute-parallel")
async def heavy_computation_task(data_item: int):
    """Simulates parallel execution workloads on individual worker nodes."""
    await asyncio.sleep(0.15)
    result = data_item * data_item
    return {"node_id": NODE_ID, "input": data_item, "result": result}