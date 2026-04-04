import random
from env.environment import SmartCityTrafficEnv
from env.tasks import get_task_config
from env.models import Action, SignalPhase, Observation, Reward

def test_determinism():
    print("Running Determinism Test...")
    config = get_task_config(1)
    
    # Run 1
    env1 = SmartCityTrafficEnv(**config)
    obs1 = env1.reset()
    score_1 = 0
    for i in range(10):
        action = Action(phase=SignalPhase.NS_GREEN, duration=10, emergency_override=False)
        _, reward, _, _ = env1.step(action)
        score_1 += reward
        
    # Run 2
    env2 = SmartCityTrafficEnv(**config)
    obs2 = env2.reset()
    score_2 = 0
    for i in range(10):
        action = Action(phase=SignalPhase.NS_GREEN, duration=10, emergency_override=False)
        _, reward, _, _ = env2.step(action)
        score_2 += reward

    assert score_1 == score_2, f"Determinism failed! {score_1} != {score_2}"
    print("✅ Determinism Test Passed")

def test_pydantic_compliance():
    print("Running Pydantic Model Compliance Test...")
    config = get_task_config(3) # Chaotic config
    env = SmartCityTrafficEnv(**config)
    
    obs = env.reset()
    assert isinstance(obs, Observation), "Reset did not return an Observation object"
    
    action = Action(phase=SignalPhase.EW_GREEN, duration=5, emergency_override=True)
    obs, reward, done, info = env.step(action)
    
    assert isinstance(obs, Observation), "Step did not return an Observation object"
    assert isinstance(reward, float), "Reward is not a float"
    assert isinstance(done, bool), "Done is not a boolean"
    assert "reward_breakdown" in info, "Missing reward_breakdown in info"
    print("✅ Pydantic Compliance Test Passed")

if __name__ == "__main__":
    test_determinism()
    test_pydantic_compliance()
    print("All tests passed successfully! The environment is robust.")
