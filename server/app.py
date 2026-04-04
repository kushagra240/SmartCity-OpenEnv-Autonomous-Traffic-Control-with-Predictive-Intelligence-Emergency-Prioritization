import uvicorn
from fastapi import FastAPI
from env.environment import SmartCityTrafficEnv
from env.models import Action

app = FastAPI(
    title="SmartCity Autonomous Traffic Control OpenEnv",
    description="API for interacting with the SmartCity Traffic Simulation Environment.",
    version="1.0.0"
)

# Start with default task 1 for baseline API
env = SmartCityTrafficEnv()

from fastapi.responses import RedirectResponse

@app.get("/")
def read_root():
    # Redirect base URL to the interactive API docs
    return RedirectResponse(url='/docs')

@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.dict()

@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def state():
    return env.state().dict()

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    main()
