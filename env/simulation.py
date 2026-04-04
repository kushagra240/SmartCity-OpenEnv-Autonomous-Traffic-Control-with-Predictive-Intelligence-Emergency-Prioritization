import random
from typing import Dict, List

class TrafficSimulation:
    def __init__(self, seed: int, inflow_rates: Dict[str, float] = None, chaotic: bool = False):
        self.seed = seed
        self.rng = random.Random(seed)
        self.chaotic = chaotic
        
        # Base inflow rates (vehicles per step). E.g. 0.2 -> 20% chance of vehicle per second
        if inflow_rates is None:
            self.base_inflow_rates = {"N": 0.2, "S": 0.2, "E": 0.2, "W": 0.2}
        else:
            self.base_inflow_rates = inflow_rates
            
        self.step_count = 0
        self.vehicles_passed_total = 0
        
        # List of wait_times for each vehicle in queue
        self.queues: Dict[str, List[int]] = {lane: [] for lane in ["N", "S", "E", "W"]}
        
        # Emergency distance: -1 means none. 0 means at the intersection. >0 means approaching.
        self.emergency_distances: Dict[str, float] = {lane: -1.0 for lane in ["N", "S", "E", "W"]}
        
        # Lookahead memory (next 5 steps)
        self.lookahead_steps = 5
        self.predicted_inflow: Dict[str, List[int]] = {lane: [] for lane in ["N", "S", "E", "W"]}
        
        # Pre-fill predictive traffic
        self._fill_predictions()

    def _fill_predictions(self):
        for lane in self.queues.keys():
            while len(self.predicted_inflow[lane]) < self.lookahead_steps:
                rate = self.base_inflow_rates[lane]
                
                if self.chaotic and self.rng.random() < 0.05:
                    rate *= 3.0 # Sudden spike
                    
                spawn_count = 0
                if self.rng.random() < rate:
                    spawn_count += 1
                if self.rng.random() < rate * 0.5:
                    spawn_count += 1
                    
                self.predicted_inflow[lane].append(spawn_count)

    def step(self, current_phase: str, phase_timer: int) -> Dict[str, int]:
        passed_this_step = {"N": 0, "S": 0, "E": 0, "W": 0}
        self.step_count += 1
        
        # Update waiting times
        for lane in self.queues.keys():
            self.queues[lane] = [w + 1 for w in self.queues[lane]]
            
        # Draw from predicted inflow
        for lane in self.queues.keys():
            incoming = self.predicted_inflow[lane].pop(0)
            for _ in range(incoming):
                self.queues[lane].append(0)
                
        self._fill_predictions()
        
        # Handle emergency spawns
        if self.chaotic and self.rng.random() < 0.01:
            target = self.rng.choice(["N", "S", "E", "W"])
            if self.emergency_distances[target] < 0:
                self.emergency_distances[target] = 300.0
                
        # Move emergencies
        for lane in self.queues.keys():
            if self.emergency_distances[lane] > 0:
                self.emergency_distances[lane] -= 15.0 # M/s speed
                if self.emergency_distances[lane] < 0:
                    self.emergency_distances[lane] = 0.0
                    
        # Outflow logic
        # 1-second delay penalty on switch (timer == 1 is dead time)
        active_lanes = ["N", "S"] if current_phase == "NS_GREEN" else ["E", "W"]
        inactive_lanes = ["E", "W"] if current_phase == "NS_GREEN" else ["N", "S"]
        
        # If there's an emergency vehicle at the intersection on an inactive lane! 
        # It's stuck and increases penalty later. The physical bounds don't allow it to cross safely.
        
        if phase_timer > 1:
            for lane in active_lanes:
                # Emergency vehicle in active lane crosses instantly
                if self.emergency_distances[lane] == 0.0:
                    self.emergency_distances[lane] = -1.0
                    passed_this_step[lane] += 1
                    self.vehicles_passed_total += 1
                
                # Try to pop a normal vehicle too
                if len(self.queues[lane]) > 0:
                    self.queues[lane].pop(0)
                    passed_this_step[lane] += 1
                    self.vehicles_passed_total += 1
                    
        return passed_this_step

    def get_lane_stats(self) -> Dict[str, Dict]:
        stats = {}
        for lane in ["N", "S", "E", "W"]:
            q = self.queues[lane]
            length = len(q)
            avg_wait = sum(q) / length if length > 0 else 0.0
            
            stats[lane] = {
                "queue_length": length,
                "avg_waiting_time": avg_wait,
                "emergency_vehicle_distance": self.emergency_distances[lane]
            }
        return stats
