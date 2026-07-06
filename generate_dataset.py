import pandas as pd
import random

data = []

# NORMAL TRAFFIC
for _ in range(2000):
    packets = random.randint(5, 50)
    duration = random.uniform(5, 60)
    bytes_count = packets * random.randint(60, 120)
    rate = packets / duration

    data.append([packets, bytes_count, duration, rate, 0])

# ATTACK TRAFFIC (REAL FLOOD)
for _ in range(2000):
    packets = random.randint(500, 5000)
    duration = random.uniform(0.1, 2)
    bytes_count = packets * random.randint(60, 120)
    rate = packets / duration

    data.append([packets, bytes_count, duration, rate, 1])

df = pd.DataFrame(data, columns=[
    "packet_count",
    "byte_count",
    "duration",
    "packet_rate",
    "label"
])

df.to_csv("data/flow_stats.csv", index=False)

print("🔥 STRONG DATASET GENERATED")
