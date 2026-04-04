from typing import Tuple, Dict, Any
from .models import Action, Observation, State, SignalPhase, LaneStats, Reward
from .simulation import TrafficSimulation
from .reward import calculate_reward

class SmartCityTrafficEnv:
    """
    OpenEnv-compliant core class handling the traffic simulation loop.
    Maps Action inputs to physical simulation ticks and returns Observation, Reward.
    """
    def __init__(self, seed: int = 42, inflow_rates: Dict[str, float] = None, chaotic: bool = False, max_steps: int = 1000):
        self.seed = seed
        self.inflow_rates = inflow_rates
        self.chaotic = chaotic
        self.max_steps = max_steps
        
        self.sim = TrafficSimulation(seed=seed, inflow_rates=inflow_rates, chaotic=chaotic)
        self.current_phase = SignalPhase.NS_GREEN
        self.time_since_last_switch = 0
        
        # Current action execution state
        self.target_phase = SignalPhase.NS_GREEN
        self.target_duration = 0
        self.current_duration = 0

    def reset(self) -> Observation:
        self.sim = TrafficSimulation(seed=self.seed, inflow_rates=self.inflow_rates, chaotic=self.chaotic)
        self.current_phase = SignalPhase.NS_GREEN
        self.time_since_last_switch = 0
        self.target_phase = SignalPhase.NS_GREEN
        self.target_duration = 0
        self.current_duration = 0
        return self._get_obs()

    def _get_obs(self) -> Observation:
        stats = self.sim.get_lane_stats()
        lanes = {
            k: LaneStats(
                queue_length=v["queue_length"],
                avg_waiting_time=v["avg_waiting_time"],
                emergency_vehicle_distance=v["emergency_vehicle_distance"]
            )
            for k, v in stats.items()
        }
        
        return Observation(
            lanes=lanes,
            current_phase=self.current_phase,
            time_since_last_switch=self.time_since_last_switch,
            predicted_inflow=self.sim.predicted_inflow.copy()
        )

    def state(self) -> State:
        return State(
            step_count=self.sim.step_count,
            rng_seed=self.sim.seed,
            vehicles_passed_total=self.sim.vehicles_passed_total,
            current_phase=self.current_phase,
            phase_timer=self.time_since_last_switch,
            lane_queues_exact={k: list(v) for k, v in self.sim.queues.items()},
            emergency_distances_exact=dict(self.sim.emergency_distances),
            predicted_inflow_exact={k: list(v) for k, v in self.sim.predicted_inflow.items()}
        )

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        if action.emergency_override:
            if self.current_phase != action.phase:
                self.current_phase = action.phase
                self.time_since_last_switch = 0
            self.target_phase = action.phase
            self.target_duration = action.duration
            self.current_duration = 0
        else:
            if self.current_duration >= self.target_duration:
                if self.current_phase != action.phase:
                    self.current_phase = action.phase
                    self.time_since_last_switch = 0
                self.target_phase = action.phase
                self.target_duration = action.duration
                self.current_duration = 0

        self.time_since_last_switch += 1
        self.current_duration += 1
        
        # Advance simulation 1 second
        passed_this_step = self.sim.step(
            current_phase=self.current_phase.value,
            phase_timer=self.time_since_last_switch
        )
        
        obs = self._get_obs()
        reward_obj = calculate_reward(self.sim.get_lane_stats(), passed_this_step)
        
        done = self.sim.step_count >= self.max_steps
        
        info = {
            "reward_breakdown": reward_obj.dict(),
            "passed_this_step": passed_this_step,
            "vehicles_passed_total": self.sim.vehicles_passed_total
        }
        
        return obs, reward_obj.total, done, info

    def close(self):
        """Cleanup resources if any."""
        pass
