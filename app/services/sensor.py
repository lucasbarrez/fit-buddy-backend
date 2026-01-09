import random
from typing import Dict, Any

class SensorService:
    """
    Mock Service to simulate retrieving data from machine sensors.
    In a real app, this would query an influxDB or an IoT API
    for the specific timeframe [start_time, end_time] and machine_id.
    """

    async def get_sensor_snapshot(self, machine_id: str, start_time: Any, end_time: Any) -> Dict[str, Any]:
        """
        Generates plausible sensor data for a set.
        """
        if not machine_id:
            return {}
        
        # Velocity based training metrics
        avg_velocity = round(random.uniform(0.3, 0.8), 2) # m/s
        peak_velocity = round(avg_velocity * 1.4, 2)
        power_output = int(random.uniform(150, 400)) # Watts
        
        # Form quality check
        rom_consistency = random.randint(85, 100) # Percentage
        asymmetry = 0
        if random.random() > 0.8:
            asymmetry = random.randint(5, 15) # Left/Right imbalance %
            
        return {
            "source": f"Sensor_{machine_id}",
            "metrics": {
                "avg_velocity_ms": avg_velocity,
                "peak_velocity_ms": peak_velocity,
                "avg_power_watts": power_output,
                "rom_consistency_pct": rom_consistency,
                "lr_asymmetry_pct": asymmetry
            },
            "status": "synced"
        }
