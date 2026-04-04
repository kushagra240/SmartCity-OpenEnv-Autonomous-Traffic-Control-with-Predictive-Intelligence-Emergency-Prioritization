from typing import Dict, Any
from .models import Reward

def calculate_reward(stats: Dict[str, Dict[str, Any]], passed: Dict[str, int]) -> Reward:
    """
    Computes a dense reward mapping the environment state to a continuous scalar.
    Parameters:
        stats: Current lane statistics.
        passed: Dictionary of how many vehicles passed this step.
    
    Reward Components:
    - wait_time_penalty: Punishes high average wait times.
    - queue_penalty: Punishes long queues.
    - throughput_bonus: Rewards cars passing through properly.
    - emergency_bonus: Harsh penalty if emergency vehicles are blocked at intersection.
    - starvation_penalty: Progressive penalty if a lane waits > 60 seconds.
    """
    alpha = -0.05
    beta = -0.1
    gamma = 1.0
    delta = -5.0 # Heavy penalty for blocked emergency vehicles
    epsilon = -2.0 # Penalty modifier for starvation
    
    total_wait = 0.0
    total_queue = 0
    total_passed = sum(passed.values())
    emergency_blocked_events = 0.0
    starvation_excess = 0.0
    
    for lane, lane_stats in stats.items():
        wait_time = lane_stats["avg_waiting_time"]
        queue_len = lane_stats["queue_length"]
        em_dist = lane_stats["emergency_vehicle_distance"]
        
        total_wait += wait_time
        total_queue += queue_len
        
        # If emergency vehicle is at 0.0 distance, it's stuck waiting!
        if em_dist == 0.0:
            emergency_blocked_events += 1.0
            
        # Starvation logic: waiting more than 60s is severely penalized
        if wait_time > 60.0:
            starvation_excess += (wait_time - 60.0) / 10.0
            
    wait_time_penalty = alpha * total_wait
    queue_penalty = beta * total_queue
    throughput_bonus = gamma * total_passed
    emergency_bonus = delta * emergency_blocked_events
    starvation_penalty = epsilon * starvation_excess
    
    total = sum([wait_time_penalty, queue_penalty, throughput_bonus, emergency_bonus, starvation_penalty])
    
    return Reward(
        total=total,
        wait_time_penalty=wait_time_penalty,
        queue_penalty=queue_penalty,
        throughput_bonus=throughput_bonus,
        emergency_bonus=emergency_bonus,
        starvation_penalty=starvation_penalty
    )
