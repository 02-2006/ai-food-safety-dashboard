import os
import asyncio
import httpx
import json
import time
from typing import List, Dict, Any
from openai import AsyncOpenAI

# --- LLM Proxy (LiteLLM) credentials injected by the OpenEnv validator ---
LLM_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
LLM_API_KEY = os.environ.get("API_KEY", os.environ.get("OPENAI_API_KEY", ""))
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o")

# --- Environment server URL (the HF Space / local server running the sim) ---
ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")

async def get_ai_action(client: AsyncOpenAI, state: Dict[str, Any], history: List[str]) -> str:
    """Uses LLM to decide the next action based on the state."""
    prompt = f"""
    You are a Food Safety AI Officer. 
    Your goal is to maximize user trust while minimizing public health risk.
    
    IMPORTANT: If hygiene data is old (>180 days) or there are many complaints, 
    you MUST investigation before promoting or flagging.
    
    ENVIRONMENT STATE:
    {json.dumps(state, indent=2)}
    
    PREVIOUS ACTIONS:
    {history}
    
    AVAILABLE ACTIONS:
    - show_safety_badge (Use if 100% sure the restaurant is safe)
    - hide_info (Use for cautious neutral stance)
    - request_inspection (Use to reveal hidden hygiene risks or refresh stale data)
    - flag_restaurant (Use to publicly mark as high-risk)

    Return ONLY the action name from the list above.
    """
    
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Food Safety AI Officer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        action = response.choices[0].message.content.strip().lower()
        for valid_action in ["show_safety_badge", "hide_info", "request_inspection", "flag_restaurant"]:
            if valid_action in action:
                return valid_action
        return "hide_info"
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return "hide_info"

async def run_task(http_client: httpx.AsyncClient, openai_client: AsyncOpenAI, task_id: str) -> float:
    print(f"\n--- RUNNING TASK: {task_id.upper()} ---", flush=True)
    
    # === STRUCTURED OUTPUT: START ===
    print(f"[START] task={task_id}", flush=True)
    
    # 1. Reset
    resp = await http_client.post(f"{ENV_URL}/reset", json={"task_id": task_id})
    resp.raise_for_status()
    state = resp.json()["observation"]
    print(f"Initial State: {state.get('restaurant_id')} | Hygiene: {state.get('hygiene_score')} | Age: {state.get('inspection_age_days')}", flush=True)
    
    # 2. Step Loop (5 steps max to allow multi-step logic)
    history = []
    step_count = 0
    last_reward = 0.0
    for i in range(5):
        action = await get_ai_action(openai_client, state, history)
        print(f"[{i+1}] Action: {action}", flush=True)
        
        step_resp = await http_client.post(f"{ENV_URL}/step", json={"action": action})
        step_resp.raise_for_status()
        data = step_resp.json()
        
        state = data["observation"]
        reward = data["reward"]
        done = data["done"]
        info = data["info"]["info"]
        
        step_count = i + 1
        last_reward = reward
        
        # === STRUCTURED OUTPUT: STEP ===
        print(f"[STEP] step={step_count} reward={reward}", flush=True)
        
        print(f"  Reward: {reward} | Reason: {info.get('reason')}", flush=True)
        history.append(action)
        if done: break
        
    # 3. Evaluate
    eval_resp = await http_client.post(f"{ENV_URL}/evaluate")
    eval_resp.raise_for_status()
    score = eval_resp.json()["score"]
    
    # === STRUCTURED OUTPUT: END ===
    print(f"[END] task={task_id} score={score} steps={step_count}", flush=True)
    
    print(f"TASK FINAL SCORE: {score}", flush=True)
    return score

async def main():
    tasks = ["easy", "medium", "hard"]
    final_scores = {}
    start_time = time.time()

    # Log which LLM endpoint we're using (helps debug proxy issues)
    print(f"LLM Base URL: {LLM_BASE_URL}", flush=True)
    print(f"ENV Base URL: {ENV_URL}", flush=True)
    print(f"Model: {MODEL_NAME}", flush=True)
    
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        # Initialize OpenAI client with the LiteLLM proxy credentials
        openai_client = AsyncOpenAI(
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
        )
        # SEQUENTIAL execution for reproducibility
        for t in tasks:
            try:
                score = await run_task(http_client, openai_client, t)
                final_scores[t] = score
            except Exception as e:
                print(f"Error in task {t}: {e}", flush=True)
                final_scores[t] = 0.0
                # Still emit structured output so validator can parse something
                print(f"[START] task={t}", flush=True)
                print(f"[STEP] step=1 reward=0.0", flush=True)
                print(f"[END] task={t} score=0.0 steps=0", flush=True)
            
    print("\n" + "="*40, flush=True)
    print("FINAL RESULTS SUMMARY", flush=True)
    print("="*40, flush=True)
    for t, s in final_scores.items():
        print(f"{t.capitalize()}: {s}", flush=True)
    
    avg_score = sum(final_scores.values()) / len(tasks)
    print(f"Global Benchmark: {avg_score:.2f}", flush=True)
    print(f"Execution Time: {time.time() - start_time:.2f}s", flush=True)
    print("="*40, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
