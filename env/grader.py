class Grader:
    """
    Evaluates the episode's total performance and outputs a deterministic score between [0.0, 1.0].
    Requires aggregating stats across the episode steps.
    """
    def __init__(self, weight_wait=0.3, weight_thru=0.4, weight_em=0.2, weight_starve=0.1):
        self.w_wait = weight_wait
        self.w_thru = weight_thru
        self.w_em = weight_em
        self.w_starve = weight_starve

    def grade(self, total_wait_sum: float, max_wait_recorded: float, total_passed: int, emergency_blocked_steps: int) -> float:
        # Strict Normalization for Hackathon Quality
        
        # total_wait_sum: ~5000 is elite. > 20000 is a failure.
        norm_wait = max(0.0, 1.0 - (total_wait_sum / 20000.0))
        
        # throughput: 1000+ is excellent for a 1000-step episode.
        norm_thru = min(1.0, total_passed / 1200.0)
        
        # Emergency: This is a CRITICAL requirement. 
        # Even 5 steps of blocking an ambulance should be heavily penalized.
        norm_em = max(0.0, 1.0 - (emergency_blocked_steps / 10.0))
        
        # Starvation: Fairness constraint. Max wait > 120s is a major failure.
        norm_starve = max(0.0, 1.0 - (max_wait_recorded / 150.0))
        
        # Weighted combination favoring Throughput and Emergency response
        score = (
            self.w_wait * norm_wait +   # 0.3
            self.w_thru * norm_thru +   # 0.4
            self.w_em * norm_em +       # 0.2
            self.w_starve * norm_starve # 0.1
        )
        
        return round(max(0.0, min(1.0, float(score))), 4)
