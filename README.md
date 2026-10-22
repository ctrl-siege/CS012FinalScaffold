# CS012 Final Project MVP Simulator Scaffolding

This repository provides a lightweight local simulation of a **Cloud-Based Distributed System** built with Python and FastAPI. It simulates key distributed system concepts—including network topology, dynamic request routing, data sharding/hybrid cloud placement, and request tracing without external cloud services or containers. 

**Note:** This is for blueprinting purposes only and it is up to you on implementing your proposed architecture.

## Prerequisites & Setup

- Python 3.9 or above

## Getting Started

1. Clone this repository 

2. Create a virtual environment
```
python -m venv venv
```

3. Activate your environment
```
venv\Scripts\activate
```

4. Install the packages
```
pip install -r requirements.txt
```

5. Launch the cluster
```
python run_cluster.py
```

## Repository Structure

* `run_cluster.py`: Main startup script to launch all cluster nodes concurrently.
* `common/`: Shared utilities including data contracts (`models.py`) and context-aware trace logging (`logger.py`).
* `coordinator/`: Source code for the Central Gateway Coordinator node (`main.py`).
* `node/`: Source code for worker nodes (`main.py`).