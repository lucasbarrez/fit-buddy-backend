from typing import List, Optional
import httpx
from app.core.config import settings

class IoTService:
    def __init__(self):
        self.base_url = settings.FIT_BUDDY_DATA_URL
        # In a real app, we might want to cache the machine list
        
    async def get_estimated_wait_time(self, machine_type_id: str) -> int:
        """
        Connects to fit-buddy-data API to get real predictions.
        Logic: 
        1. List all machines.
        2. Filter those matching 'machine_type_id' (Naive contains match).
        3. Get prediction for each.
        4. Return the BEST availability (min wait time).
        """
        try:
            async with httpx.AsyncClient() as client:
                # 1. Get All Machines
                resp = await client.get(f"{self.base_url}/api/machine/list", timeout=5.0)
                if resp.status_code != 200:
                    print(f"⚠️ IoT API Error (List): {resp.status_code}")
                    return 0 # Fallback 
                
                all_machines = resp.json().get("machines", [])
                
                # 2. Naive Filter
                # We assume machine_type_id (e.g. "DC_BENCH") is widely used in the ID (e.g. "DC_BENCH_001")
                candidates = [m for m in all_machines if machine_type_id in m]
                
                if not candidates:
                    return 0 

                # 3. Check Prediction for each
                wait_times = []
                for mid in candidates:
                    p_resp = await client.get(f"{self.base_url}/api/machine/{mid}/prediction", timeout=3.0)
                    if p_resp.status_code == 200:
                        data = p_resp.json().get("data", {})
                        if data.get("available"):
                            return 0 # Found one free!
                        else:
                            wait_times.append(data.get("time_to_wait", 0))
                
                if not wait_times:
                     return 0
                     
                return min(wait_times)
                
        except Exception as e:
            print(f"⚠️ IoT Service Connection Error: {e}")
            return 0 # Fail open
