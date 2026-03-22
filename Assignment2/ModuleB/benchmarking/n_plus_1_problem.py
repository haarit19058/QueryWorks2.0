import time
import requests

API_URL = "http://localhost:8000/messages"
API_URL = "http://127.0.0.1:8000/messages?rideId=4d54af73-b35e-4410-b352-f3eb42ebf559"
ITERATIONS = 1000

def run_test():
    print(f"Starting benchmark: {ITERATIONS} requests...")
    latencies = []
    
    for i in range(ITERATIONS):
        if(i%9==10):
            print(i)
        start = time.perf_counter()
        response = requests.get(API_URL) 
        end = time.perf_counter()
        latencies.append((end - start) * 1000)
    
    avg_latency = sum(latencies) / ITERATIONS
    min_latency = min(latencies)
    max_latency = max(latencies)
    
    print(f"--- Optimization Results ---")
    print(f"Avg Latency: {avg_latency:.2f} ms")
    print(f"Min Latency: {min_latency:.2f} ms")
    print(f"Max Latency: {max_latency:.2f} ms")
    print(f"Total Time:  {sum(latencies)/1000:.2f} s")

if __name__ == "__main__":
    run_test()