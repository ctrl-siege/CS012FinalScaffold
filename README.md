# CS012 Final Project Scaffolding

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