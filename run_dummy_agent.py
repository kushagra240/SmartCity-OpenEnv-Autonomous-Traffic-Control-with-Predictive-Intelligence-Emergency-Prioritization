import time
import random
from env.environment import SmartCityTrafficEnv
from env.tasks import get_task_config
from env.models import Action, SignalPhase

def simulate_dummy_agent():
    print("--- Starting Dummy Agent Simulation on Task 3 (Emergency + Chaos) ---")
    config = get_task_config(3)
    env = SmartCityTrafficEnv(**config)
    
    obs = env.reset()
    print("[START] Simulation initialized")
    
    for i in range(15):
        # Dummy Logic: Switch phase if queue gets too long on a red light, otherwise hold
        # For simplicity, we just alternate randomly or based on a basic heuristic
        
        N_queue = obs.lanes['N'].queue_length
        E_queue = obs.lanes['E'].queue_length
        
        # Check emergencies
        em_hazard = any(lane.emergency_vehicle_distance >= 0.0 for lane in obs.lanes.values())
        
        target_phase = SignalPhase.NS_GREEN if N_queue >= E_queue else SignalPhase.EW_GREEN
        
        if em_hazard:
            # aggressive override
            target_phase = SignalPhase.NS_GREEN if max(obs.lanes['N'].emergency_vehicle_distance, obs.lanes['S'].emergency_vehicle_distance) >= 0.0 else SignalPhase.EW_GREEN
            
        action = Action(
            phase=target_phase,
            duration=10,
            emergency_override=em_hazard
        )
        
        obs, reward, done, info = env.step(action)
        print(f"[STEP] idx={i} | Phase={action.phase.value} | Reward={reward:.2f} | Em_active={em_hazard} | Passed_Total={info['vehicles_passed_total']}")
        
        time.sleep(0.1) # Simulate real-time logging feel
        
    print("[END] Dummy agent completed the trajectory.")

if __name__ == "__main__":
    simulate_dummy_agent()
