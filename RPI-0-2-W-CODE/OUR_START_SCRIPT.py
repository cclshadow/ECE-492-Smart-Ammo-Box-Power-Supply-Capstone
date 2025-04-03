import time
from datetime import datetime

while True:
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"Current time: {current_time}")
    time.sleep(1)  # Wait for 1 second before next print

