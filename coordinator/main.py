import os
import httpx
import asyncio
from typing import List
from fastapi import FastAPI, Header, HTTPException, Request
from common.models import DataPayload, DistributedResponse
from common.logger import get_logger, trace_id_var, generate_trace_id

app = FastAPI(title="Distributed Coordinator Node")
logger = get_logger("Coordinator")

# Configured worker endpoints
WORKER_NODES = os.getenv("WORKERS", "http://localhost:8001,http://localhost:8002,http://localhost:8003").split(",")

@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    # Generates or captures X-Trace-ID and propagates it across all hop requests
    trace_id = request.headers.get("X-Trace-ID") or generate_trace_id()
    trace_id_var.set(trace_id)
    logger.info(f"Incoming Gateway Request: {request.method} {request.url.path}")
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response

def get_target_node_for_key(key: str) -> str:
    """Consistently maps a data key to a specific node (Key Sharding Simulation)."""
    hash_value = sum(ord(char) for char in key)
    selected_index = hash_value % len(WORKER_NODES)
    return WORKER_NODES[selected_index]

# Distributed Cluster Management Endpoints

@app.get("/cluster/health")
async def cluster_health():
    """Checks the operational status of all worker nodes in parallel."""
    headers = {"X-Trace-ID": trace_id_var.get()}
    async with httpx.AsyncClient(timeout=2.0) as client:
        tasks = [client.get(f"{node}/health", headers=headers) for node in WORKER_NODES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        status_report = {}
        for node, resp in zip(WORKER_NODES, results):
            if isinstance(resp, Exception):
                status_report[node] = {"status": "UNREACHABLE", "error": str(resp)}
            else:
                status_report[node] = resp.json()
                
    return {"cluster_status": status_report, "trace_id": trace_id_var.get()}

@app.post("/api/v1/write")
async def write_data(payload: DataPayload):
    """Shards incoming write requests based on key hash or sensitivity."""
    if payload.is_sensitive:
        target_node = WORKER_NODES[0]  # Force to Private VPC Node
    else:
        target_node = get_target_node_for_key(payload.key)
        
    logger.info(f"Routing Key '{payload.key}' -> Target Node: {target_node}")
    headers = {"X-Trace-ID": trace_id_var.get(), "X-Network-Zone": "PRIVATE_VPC" if payload.is_sensitive else "PUBLIC"}
    
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            resp = await client.post(f"{target_node}/store", json=payload.model_dump(), headers=headers)
            return resp.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Target node {target_node} unavailable: {exc}")

@app.get("/api/v1/read/{key}")
async def read_data(key: str):
    """Directly routes request to partition hosting the key."""
    target_node = get_target_node_for_key(key)
    headers = {"X-Trace-ID": trace_id_var.get()}
    
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            resp = await client.get(f"{target_node}/read/{key}", headers=headers)
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Key not found in distributed store.")
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail=f"Worker node {target_node} unavailable.")