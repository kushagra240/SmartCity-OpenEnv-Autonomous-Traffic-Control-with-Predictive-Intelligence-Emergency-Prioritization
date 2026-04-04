# SmartCity Autonomous Traffic Control
## OpenEnv Environment with Predictive Intelligence & Emergency Prioritization

### Environment Description and Motivation
The SmartCity Autonomous Traffic Control environment is a state-of-0the-art simulation built on the OpenEnv spec. Its primary motivation is to train robust AI agents capable of handling complex urban traffic intersections dynamically. Unlike traditional timed traffic lights, this environment focuses on optimizing traffic flow, minimizing average wait times, handling uneven rush-hour imbalances, and proactively accommodating emergency vehicles using predictive intelligence.

### Action and Observation Space Definitions

#### Observation Space
The observation space provides a rich representation of the intersection's current state:
* `lanes` (Dict): Statistics for each lane (N, S, E, W), including queue lengths and emergency vehicle proximities.
* `current_phase` (String): The currently active green light phase (`NS_GREEN` or `EW_GREEN`).
* `time_since_last_switch` (Integer): Time in seconds since the last phase change.
* `predicted_inflow` (Dict): Forecasted inflow of vehicles for the next 5 time steps for each lane.

#### Action Space
The agent responds by configuring the traffic signals:
* `phase` (String): The target phase to activate (`NS_GREEN` or `EW_GREEN`).
* `duration` (Integer): Time duration to hold the phase (1-60 seconds).
* `emergency_override` (Boolean): A flag to forcibly override regular scheduling to prioritize emergency vehicles.

### Task Descriptions with Expected Difficulty

The environment features three structured tasks of ascending complexity:

1. **Task 1: Basic Flow Optimization** (Easy)
   * *Description:* Characterized by stable, uniform traffic flow.
   * *Goal:* Identify the baseline cycle times to minimize average wait time and ensure max throughput.
2. **Task 2: Rush Hour Imbalance** (Medium)
   * *Description:* Experiencing uneven inflow simulating morning or evening commutes.
   * *Goal:* Dynamically adjust timings to clear unbalanced queues efficiently without starving low-traffic lanes.
3. **Task 3: Emergency + Chaos** (Hard)
   * *Description:* Random traffic spikes accompanied by the unpredictable approach of emergency vehicles.
   * *Goal:* Successfully balance traffic flow while leveraging the `emergency_override` to clear paths for critical response vehicles instantly.

### Setup and Usage Instructions

1. **Install Dependencies:**
   Ensure you have Python 3.9+ installed. Set up the virtual environment and install the required dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Dummy Baseline Agent:**
   To verify your installation, run the provided heuristic dummy agent:
   ```bash
   python run_dummy_agent.py
   ```

3. **Run Inference & Evaluation:**
   Set the appropriate environment variables and run the inference script to evaluate an LLM controller:
   ```bash
   export API_BASE_URL="<your_api>"
   export HF_TOKEN="<your_token>"
   export MODEL_NAME="<model_name>"
   python inference.py
   ```

4. **Start the API Server (Optional):**
   ```bash
   uvicorn server.app:app --host 0.0.0.0 --port 8000
   ```

### Baseline Scores
* **Dummy Heuristic Agent:** ~0.2 - 0.3 (Normalized Score)
* **Target Success Threshold:** >= 0.5 (Normalized Score)
* **Max Possible Score Context:** 1.0 (Dense reward mapping scaling approx 2.0/step as excellent config)
