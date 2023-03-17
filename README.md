# Safety Violation Simulator
This package contains the `SafetyViolationSimulator` class in `safety_violation_sim.py` file.
A `SafetyViolationSimulator` class simulates times to safety violations given
    parameters for the blockchain,
    reset policy (time to wait before resetting the block to build the adversarial chain on), and
    number of trials to run with each reset policy
to record expected values of time for a safety violation for different reset policies and
to find the optimal reset policy that minimizes the time for a safety violation.

### Configuration
Configure the simulator by changing the parameters under `if __name__ == "__main__":` in `safety_violation_sim.py`

### Run
`python safety_violation_sim.py`