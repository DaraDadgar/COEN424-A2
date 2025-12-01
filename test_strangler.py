import requests
import threading
from collections import Counter

GATEWAY_URL = "http://localhost:5000/users"
NUM_REQUESTS = 200
TIMEOUT = 5

counter = Counter()
errors = 0


def make_request(i):
    global errors
    try:
        r = requests.get(GATEWAY_URL, timeout=TIMEOUT)
        version = r.headers.get("X-Service-Version", "unknown")
        counter[version] += 1
    except Exception as e:
        print(f"Request {i} failed: {e}")
        errors += 1


threads = []
for i in range(NUM_REQUESTS):
    t = threading.Thread(target=make_request, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("Results:")
for k, v in counter.items():
    print(f"  {k}: {v} ({v/NUM_REQUESTS*100:.1f}%)")
print(f"  errors: {errors}")
