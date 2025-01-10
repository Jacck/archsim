import time
from enum import Enum
from typing import Callable, Any
import random
import matplotlib.pyplot as plt
import numpy as np

class CircuitState(Enum):
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"      # Circuit is broken
    HALF_OPEN = "HALF_OPEN"  # Testing if service is back

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        half_open_timeout: float = 5.0
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.last_attempt_time = 0
    
    def can_execute(self) -> bool:
        now = time.time()
        
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            if now - self.last_failure_time >= self.reset_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
            
        if self.state == CircuitState.HALF_OPEN:
            if now - self.last_attempt_time >= self.half_open_timeout:
                return True
            return False
            
        return False

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            
    def execute(self, func: Callable[[], Any]) -> Any:
        if not self.can_execute():
            raise Exception(f"Circuit Breaker is {self.state.value}. Service unavailable.")
            
        self.last_attempt_time = time.time()
        
        try:
            result = func()
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e

# Demo of the circuit breaker
def unstable_service() -> str:
    """Simulates an unstable service that fails randomly"""
    if random.random() < 0.7:  # 70% chance of failure
        raise Exception("Service failed!")
    return "Service succeeded!"

def visualize_simulation(attempts, states, failures, results):
    # Create figure and axis
    plt.figure(figsize=(15, 8))
    
    # Create a color map for states
    state_colors = {
        'CLOSED': 'green',
        'HALF_OPEN': 'yellow',
        'OPEN': 'red'
    }
    
    # Plot circuit state
    plt.subplot(3, 1, 1)
    state_values = [1 if s == 'CLOSED' else 0.5 if s == 'HALF_OPEN' else 0 for s in states]
    plt.plot(attempts, state_values, 'o-', label='Circuit State')
    plt.yticks([0, 0.5, 1], ['OPEN', 'HALF_OPEN', 'CLOSED'])
    plt.grid(True)
    plt.title('Circuit Breaker State Over Time')
    plt.xlabel('Attempt Number')
    plt.ylabel('State')
    
    # Plot failure count
    plt.subplot(3, 1, 2)
    plt.plot(attempts, failures, 'ro-', label='Failure Count')
    plt.grid(True)
    plt.title('Failure Count Over Time')
    plt.xlabel('Attempt Number')
    plt.ylabel('Count')
    
    # Plot service results
    plt.subplot(3, 1, 3)
    success_mask = [r == 'Success' for r in results]
    failure_mask = [r == 'Failure' for r in results]
    blocked_mask = [r == 'Blocked' for r in results]
    
    plt.scatter(np.array(attempts)[success_mask], [1] * sum(success_mask), 
               color='green', label='Success', marker='o')
    plt.scatter(np.array(attempts)[failure_mask], [0] * sum(failure_mask), 
               color='red', label='Failure', marker='x')
    plt.scatter(np.array(attempts)[blocked_mask], [0.5] * sum(blocked_mask), 
               color='gray', label='Blocked', marker='s')
    
    plt.grid(True)
    plt.title('Service Call Results')
    plt.xlabel('Attempt Number')
    plt.yticks([0, 0.5, 1], ['Failure', 'Blocked', 'Success'])
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('circuit_breaker_simulation.png')
    plt.close()

def main():
    # Create circuit breaker with lower thresholds for demo
    breaker = CircuitBreaker(
        failure_threshold=3,  # Open after 3 failures
        reset_timeout=5.0,    # Try to reset after 5 seconds
        half_open_timeout=1.0 # Allow retry every 1 second in half-open
    )
    
    # Lists to store simulation data
    attempts = []
    states = []
    failures = []
    results = []
    
    # Run service calls in a loop
    for i in range(20):
        attempt_num = i + 1
        attempts.append(attempt_num)
        states.append(breaker.state.value)
        failures.append(breaker.failure_count)
        
        print(f"\nAttempt {attempt_num}")
        print(f"Circuit State: {breaker.state.value}")
        print(f"Failure Count: {breaker.failure_count}")
        
        try:
            result = breaker.execute(unstable_service)
            print(f"Result: {result}")
            results.append('Success')
        except Exception as e:
            print(f"Error: {str(e)}")
            if "Circuit Breaker is" in str(e):
                results.append('Blocked')
            else:
                results.append('Failure')
            
        time.sleep(1)  # Wait between attempts
    
    # Visualize the simulation results
    visualize_simulation(attempts, states, failures, results)

if __name__ == "__main__":
    main()