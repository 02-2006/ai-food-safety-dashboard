import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from server.environment_core.environment import get_env
from server.environment_core.actions import Action
from server.environment_core.tasks import TASKS
from server.environment_core.graders import GRADERS
from server.environment_core.state import RestaurantState

app = FastAPI(title="AI Food Safety Transparency Environment")

class ObservationModel(BaseModel):
    restaurant: RestaurantState

class ResetResponse(BaseModel):
    observation: ObservationModel
    info: str

class StepResponse(BaseModel):
    observation: ObservationModel
    reward: float
    done: bool
    info: Dict[str, Any]

class StateResponse(BaseModel):
    observation: ObservationModel

# Paths relative to this file
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Serve Static Files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def read_index():
    return FileResponse(str(STATIC_DIR / "index.html"))

# Global environment singleton access
env = get_env()
current_task_id: Optional[str] = None
trajectory: List[Dict[str, Any]] = []

class ResetRequest(BaseModel):
    task_id: Optional[str] = "easy"

class StepRequest(BaseModel):
    action: str

@app.post("/reset", response_model=ResetResponse)
async def reset(req: ResetRequest = ResetRequest()):
    global current_task_id, trajectory
    if req.task_id and req.task_id.lower() not in TASKS:
        raise HTTPException(status_code=400, detail=f"Task {req.task_id} not found. Available: {list(TASKS.keys())}")
    
    current_task_id = req.task_id.lower() if req.task_id else "easy"
    initial_state = TASKS[current_task_id]()
    
    # Reset the singleton environment
    obs = env.reset(initial_state)
    trajectory = [] # Clear history
    
    return {
        "observation": obs, 
        "info": f"Environment reset to task: {current_task_id}"
    }

@app.post("/step", response_model=StepResponse)
async def step(req: StepRequest):
    global trajectory
    try:
        action_enum = Action(req.action)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid action: {req.action}. Available: {[a.value for a in Action]}")
    
    obs, reward, done, info = env.step(action_enum)
    
    # Track trajectory for evaluation
    trajectory.append({
        "action": req.action,
        "reward": reward,
        "state": obs
    })
    
    return {
        "observation": obs,
        "reward": clamp_score(reward),
        "done": done,
        "info": info
    }

@app.get("/state", response_model=StateResponse)
async def get_state():
    curr_state = env.state()
    print(f"STATE DEBUG [ENV {id(env)}]:", curr_state)
    return {"observation": curr_state}

def clamp_score(score: float) -> float:
    """Pass-through for binary scores (0 or 1)."""
    return round(float(score))

@app.post("/evaluate")
async def evaluate():
    """Evaluate the current trajectory based on the task grader."""
    global current_task_id, trajectory
    if not current_task_id or not trajectory:
        raise HTTPException(status_code=400, detail="No active task or trajectory to evaluate.")
    
    grader = GRADERS.get(current_task_id)
    if not grader:
        raise HTTPException(status_code=500, detail="Grader not found for current task.")
    
    score = grader(trajectory)
    return {
        "task": current_task_id,
        "score": clamp_score(score),
        "steps": len(trajectory)
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

def main():
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
