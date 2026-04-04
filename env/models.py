from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class SignalPhase(str, Enum):
    NS_GREEN = "NS_GREEN"
    EW_GREEN = "EW_GREEN"

class Action(BaseModel):
    phase: SignalPhase = Field(..., description="The main phase to set the signal to")
    duration: int = Field(..., ge=1, le=60, description="Duration to keep the phase (1-60s)")
    emergency_override: bool = Field(default=False, description="Whether to aggressively override for an emergency vehicle")

class LaneStats(BaseModel):
    queue_length: int = Field(..., description="Number of waiting vehicles")
    avg_waiting_time: float = Field(..., description="Average wait time of vehicles in queue")
    emergency_vehicle_distance: float = Field(default=-1.0, description="Distance of emergency vehicle. -1.0 if none.")

class Observation(BaseModel):
    lanes: Dict[str, LaneStats] = Field(..., description="Lane statistics for N, S, E, W")
    current_phase: SignalPhase = Field(..., description="Currently active signal phase")
    time_since_last_switch: int = Field(..., description="Time elapsed since the phase last changed")
    predicted_inflow: Dict[str, List[int]] = Field(..., description="Predicted number of incoming cars in the next 5 steps per lane")

class Reward(BaseModel):
    total: float
    wait_time_penalty: float
    queue_penalty: float
    throughput_bonus: float
    emergency_bonus: float
    starvation_penalty: float

class State(BaseModel):
    step_count: int
    rng_seed: int
    vehicles_passed_total: int
    current_phase: SignalPhase
    phase_timer: int
    lane_queues_exact: Dict[str, List[int]]  # Wait time of each individual car
    emergency_distances_exact: Dict[str, float]
    predicted_inflow_exact: Dict[str, List[int]]
