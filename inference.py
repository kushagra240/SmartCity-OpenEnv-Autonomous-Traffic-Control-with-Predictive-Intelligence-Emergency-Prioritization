import os
import json
import asyncio
import textwrap
from typing import List, Optional
from openai import OpenAI
from env.environment import SmartCityTrafficEnv
from env.tasks import get_task_config
from env.models import Action, SignalPhase

# Mandatory Configuration
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "gpt-4o-mini"
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "dummy_key")

BENCHMARK = "smartcity-traffic-control"
MAX_STEPS = 20 # Baseline restriction for speed
SUCCESS_SCORE_THRESHOLD = 0.5

# Heuristic for score normalization [0, 1]
# Based on dense rewards where ~2.0/step is excellent.
MAX_TOTAL_REWARD = MAX_STEPS * 3.0

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}", flush=True)

def get_model_action(client: OpenAI, obs_json: str) -> Action:
    system_prompt = (
        "You are an AI autonomous traffic controller for a 4-way intersection. "
        "You receive observations including queues, predicted inflow, and emergency vehicle distances. "
        "Output ONLY a valid JSON object matching this schema: "
        '{"phase": "NS_GREEN" or "EW_GREEN", "duration": int (1-60), "emergency_override": bool}.'
    )
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Observation: {obs_json}"}
            ],
            response_format={"type": "json_object"}
        )
        raw_content = completion.choices[0].message.content
        parsed = json.loads(raw_content)
        return Action(
            phase=SignalPhase(parsed.get("phase", "NS_GREEN")),
            duration=int(parsed.get("duration", 10)),
            emergency_override=bool(parsed.get("emergency_override", False))
        )
    except Exception:
        return Action(phase=SignalPhase.NS_GREEN, duration=10, emergency_override=False)

async def run_task(client: OpenAI, task_id: int):
    task_name = f"task_{task_id}"
    config = get_task_config(task_id)
    # Ensure our max steps in environment matches inference script
    config['max_steps'] = MAX_STEPS
    env = SmartCityTrafficEnv(**config)
    
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)
    
    try:
        obs = env.reset()
        for step in range(1, MAX_STEPS + 1):
            action = get_model_action(client, obs.json())
            
            obs, reward, done, info = env.step(action)
            
            rewards.append(reward)
            steps_taken = step
            
            log_step(step=step, action=action.json(), reward=reward, done=done, error=None)
            
            if done:
                break
        
        total_reward = sum(rewards)
        score = total_reward / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
        score = min(max(score, 0.0001), 0.9999)
        success = score >= SUCCESS_SCORE_THRESHOLD
        
    finally:
        env.close()
        log_end(success=success, steps=steps_taken, rewards=rewards)

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    for tid in [1, 2, 3]:
        await run_task(client, tid)

if __name__ == "__main__":
    asyncio.run(main())
