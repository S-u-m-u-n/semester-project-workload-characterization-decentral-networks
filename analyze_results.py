import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys


directory = sys.argv[1]

# Function to parse timestamp from filename
def parse_timestamp(filename):
    basename = os.path.basename(filename)
    timestamp_str = re.search(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv", basename).group()[:-4]
    return datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

# Read CSV files and store their data in a list of dictionaries
data = []
for file in glob.glob(str(directory) + "/en.wikipedia-on-ipfs.org_CID_providers_*.csv"):
    if re.match(r"en\.wikipedia-on-ipfs\.org_CID_providers_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv", os.path.basename(file)):
        df = pd.read_csv(file)
        timestamp = parse_timestamp(file)
        total = len(df)
        reachable = len(df[df["Reachable"] == True])
        not_reachable = total - reachable
        data.append({"timestamp": timestamp, "total": total, "reachable": reachable, "not_reachable": not_reachable})

# Sort the data by timestamp
data.sort(key=lambda x: x["timestamp"])

# Extract data for plotting
timestamps = [entry["timestamp"] for entry in data]
totals = [entry["total"] for entry in data]
reachables = [entry["reachable"] for entry in data]
not_reachables = [entry["not_reachable"] for entry in data]

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(timestamps, totals, label="Total number of Providers", color='black')
plt.plot(timestamps, reachables, label="Reachable", color='green')
plt.plot(timestamps, not_reachables, label="Non-reachable", color='red')
plt.xlabel("Timestamp")
plt.ylabel("Total number of providers")
plt.title("Development of providers over time")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('results.png')
# plt.show()
