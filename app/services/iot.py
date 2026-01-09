import random
from typing import Optional

class IoTService:
    """
    Mock Service to simulate IoT sensor data from gym machines.
    In a real scenario, this would call an external API (e.g., SensorAPI).
    """
    
    def __init__(self):
        # Configuration for simulation
        # chance of being busy: 0.0 to 1.0
        self.busy_probability = 0.3 
    
    async def get_estimated_wait_time(self, machine_type_id: str) -> int:
        """
        Get estimated wait time in MINUTES for a given machine type.
        Returns 0 if available immediately.
        """
        if not machine_type_id:
            return 0
            
        # Simulate logic:
        # Some machines are more popular
        popular_machines = ["DC_BENCH", "SQUAT_RACK", "CABLE_STATION"]
        
        is_popular = any(p in machine_type_id.upper() for p in popular_machines)
        
        # Base probability check
        threshold = self.busy_probability + (0.4 if is_popular else 0.0)
        
        if random.random() < threshold:
            # It's busy. Return random wait between 2 and 15 minutes
            return random.randint(2, 15)
        
        return 0

    async def get_all_machines_status(self) -> dict[str, int]:
        """
        Returns a snapshot of all tracked machines and their wait times.
        Useful for a dashboard.
        """
        # Mocking a set of machines
        machines = ["DC_BENCH", "SQUAT_RACK", "LEG_PRESS", "DUMBBELLS"]
        return {m: await self.get_estimated_wait_time(m) for m in machines}
