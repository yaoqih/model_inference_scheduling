import uvicorn
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import random
import time

app = FastAPI(
    title="Test Node Server",
    description="A mock server for simulating a model inference node.",
    version="1.0.0"
)

# --- Mock Data Store ---
# Simulates the state of GPUs and running models on the node
MOCK_GPU_COUNT = 2
MOCK_GPU_MEMORY_TOTAL = 24 * 1024  # 24GB in MB
MOCK_GPU_POWER_LIMIT = 450  # 450W

# Initial state for running models (gpu_id -> model_info)
running_models: Dict[int, Dict[str, Any]] = {}

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Test Node Server is running."}

@app.get("/api/v1/gpus", response_model=List[Dict[str, Any]])
def get_gpu_status():
    """Returns detailed status for all GPUs on the node."""
    gpus = []
    for i in range(MOCK_GPU_COUNT):
        is_model_running = i in running_models
        
        # Simulate dynamic load and usage
        base_load = random.uniform(15, 40) if is_model_running else random.uniform(1, 5)
        memory_used = random.uniform(8 * 1024, 16 * 1024) if is_model_running else random.uniform(200, 800)
        power_usage = random.uniform(200, 350) if is_model_running else random.uniform(50, 100)

        gpus.append({
            "gpu_id": i,
            "load": round(base_load + random.uniform(-2, 2), 2),
            "memory_used": round(memory_used, 2),
            "memory_total": MOCK_GPU_MEMORY_TOTAL,
            "power_usage": round(power_usage, 2),
            "power_limit": MOCK_GPU_POWER_LIMIT,
            "temperature": random.uniform(45, 75)
        })
    return gpus

@app.get("/api/v1/models/status", response_model=List[Dict[str, Any]])
def get_all_model_statuses():
    """Returns the status of all running models."""
    return list(running_models.values())

@app.post("/api/v1/models/start")
async def start_model(request: Dict[str, Any]):
    """Starts a model on a specified GPU."""
    model_name = request.get("model_name")
    gpu_id = request.get("gpu_id")

    if model_name is None or gpu_id is None:
        raise HTTPException(status_code=400, detail="model_name and gpu_id are required.")
    
    if gpu_id in running_models:
        raise HTTPException(status_code=409, detail=f"GPU {gpu_id} is already in use by model {running_models[gpu_id]['model_name']}.")

    # Simulate model startup time
    await asyncio.sleep(2) 

    instance = {
        "model_name": model_name,
        "gpu_id": gpu_id,
        "pid": random.randint(10000, 99999),
        "status": "RUNNING",
        "start_time": time.time()
    }
    running_models[gpu_id] = instance
    return {"status": "success", "message": f"Model '{model_name}' started on GPU {gpu_id}.", "instance": instance}

@app.post("/api/v1/models/stop")
async def stop_model(request: Dict[str, Any]):
    """Stops a model on a specified GPU."""
    gpu_id = request.get("gpu_id")

    if gpu_id is None:
        raise HTTPException(status_code=400, detail="gpu_id is required.")
        
    if gpu_id not in running_models:
        raise HTTPException(status_code=404, detail=f"No model found running on GPU {gpu_id}.")

    # Simulate model stop time
    await asyncio.sleep(1)
    
    stopped_model = running_models.pop(gpu_id)
    return {"status": "success", "message": f"Model '{stopped_model['model_name']}' stopped on GPU {gpu_id}."}


if __name__ == "__main__":
    # To run this server: uvicorn test_node_server:app --host 0.0.0.0 --port 6004 --reload
    uvicorn.run(app, host="0.0.0.0", port=6004)