import httpx
from typing import Dict, Any
from app.core.config import settings
from datetime import datetime

class SensorService:
    """
    Connects to fit-buddy-data API to retrieve metrics.
    """
    def __init__(self):
        self.base_url = settings.FIT_BUDDY_DATA_URL

    async def get_sensor_snapshot(self, machine_id: str, start_time: Any, end_time: Any) -> Dict[str, Any]:
        """
        Fetches sensor data for a set timeframe.
        """
        if not machine_id:
            return {}

        # Format timestamps to ISO
        s_iso = start_time.isoformat() if isinstance(start_time, datetime) else str(start_time)
        e_iso = end_time.isoformat() if isinstance(end_time, datetime) else str(end_time)

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.base_url}/api/sensor/metrics",
                    params={
                        "machine_id": machine_id,
                        "start_time": s_iso,
                        "end_time": e_iso
                    },
                    timeout=5.0
                )
                
                if resp.status_code == 200:
                    payload = resp.json()
                    return payload.get("data", {})
                
                print(f"Sensor API Error: {resp.status_code} - {resp.text}")
                return {}

        except Exception as e:
            print(f"Sensor Service Connection Error: {e}")
            return {}
