import subprocess
import sys
import os

def main():
    print("==================================================")
    print(" Starting Simulated Cloud Distributed Cluster...")
    print("==================================================")
    
    processes = []
    
    # Define your worker nodes here
    # This is an example (simulating 3 workers, 2 public workers and 1 private worker)
    workers = [
        {"id": "Worker-1-Private", "port": "8001", "is_private": "true"},
        {"id": "Worker-2-Public", "port": "8002", "is_private": "false"},
        {"id": "Worker-3-Public", "port": "8003", "is_private": "false"},
    ]
    
    for w in workers:
        print(f"[Cluster Manager] Starting {w['id']} on http://localhost:{w['port']}")
        cmd = [
            sys.executable, "-m", "uvicorn", "node.main:app",
            "--host", "0.0.0.0",
            "--port", w["port"],
            "--log-level", "warning"
        ]
        env = {
            "NODE_ID": w["id"],
            "PORT": w["port"],
            "IS_PRIVATE": w["is_private"]
        }
        p = subprocess.Popen(cmd, env={**os.environ, **env})
        processes.append(p)

    # Central Coordinator Node
    print("[Cluster Manager] Starting Central Coordinator Gateway on http://localhost:8000")
    coord_cmd = [
        sys.executable, "-m", "uvicorn", "coordinator.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "info"
    ]
    coord_env = {
        "WORKERS": "http://localhost:8001,http://localhost:8002,http://localhost:8003"
    }
    p_coord = subprocess.Popen(coord_cmd, env={**os.environ, **coord_env})
    processes.append(p_coord)

    print("\n[Cluster Online] Master Gateway: http://localhost:8000")
    print("Interactive Swagger Docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop all cluster processes.\n")

    try:
        p_coord.wait()
    except KeyboardInterrupt:
        print("\n[Cluster Manager] Shutting down all cluster nodes...")
        for p in processes:
            p.terminate()
        print("[Cluster Manager] Cluster stopped successfully.")

if __name__ == "__main__":
    main()