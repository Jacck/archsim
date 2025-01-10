import time
from enum import Enum
from typing import Callable, Any
import random

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

def main():
    # Create circuit breaker with lower thresholds for demo
    breaker = CircuitBreaker(
        failure_threshold=3,  # Open after 3 failures
        reset_timeout=5.0,    # Try to reset after 5 seconds
        half_open_timeout=1.0 # Allow retry every 1 second in half-open
    )
    
    # Run service calls in a loop
    for i in range(20):
        print(f"\nAttempt {i + 1}")
        print(f"Circuit State: {breaker.state.value}")
        
        try:
            result = breaker.execute(unstable_service)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
            
        time.sleep(1)  # Wait between attempts

if __name__ == "__main__":
    main()