# scripts/monitor_render.py
import requests
import time
from datetime import datetime

def monitor_service():
    url = "https://argfy-backend.onrender.com/health"
    
    while True:
        try:
            response = requests.get(url, timeout=30)
            status = "🟢 UP" if response.status_code == 200 else f"🔴 DOWN ({response.status_code})"
            print(f"{datetime.now()}: {status}")
        except Exception as e:
            print(f"{datetime.now()}: 🔴 ERROR - {e}")
        
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    monitor_service()