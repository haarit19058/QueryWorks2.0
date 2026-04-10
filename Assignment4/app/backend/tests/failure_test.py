import requests
import time

BASE_URL = "http://localhost:8000"
TEST_RIDE_ID = "0071a175-9546-41e3-95a3-c55b73ab1a5e" 

def simulate_mid_transaction_failure():
    print(f"Attempting to complete ride {TEST_RIDE_ID}...")
    
    payload = {
        "status": "COMPLETED",
        "platform": "Uber",
        "price": 450
    }

    try:
        response = requests.patch(
            f"{BASE_URL}/rides/{TEST_RIDE_ID}/status", 
            json=payload, 
            timeout=0.01  # Forces a local timeout mid-process
        )
    except requests.exceptions.Timeout:
        print("!!! Simulated Client Timeout/Crash !!!")
    except Exception as e:
        print(f"Caught: {e}")

if __name__ == "__main__":
    simulate_mid_transaction_failure()