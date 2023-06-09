import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys

sample_size = int(sys.argv[1])

def evaluate_data(language):
    # Read CSV files and store their data in a list of dictionaries
    data = []
    # pattern = r"^[a-z]{2}\.wikipedia-on-ipfs\.org_links_1_CID_providers_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv$"
    pattern = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_cleaned\.csv$"
    for file in glob.glob("./data/" + str(language) + "/" + str(sample_size) + "/CID/*.csv"):
        # print(file)
        if re.match(pattern, os.path.basename(file)):
            print(file)
            df = pd.read_csv(file)
            timestamp = parse_timestamp(file)
            total = len(df)
            unavailable = len(df[df["Number of Providers"] == 0])
            available = total - unavailable
            data.append({"timestamp": timestamp, "total": total, "available": available, "unavailable": unavailable})

    # Sort the data by timestamp
    data.sort(key=lambda x: x["timestamp"])

    # Extract data for plotting
    timestamps = [entry["timestamp"] for entry in data]
    totals = [entry["total"] for entry in data]
    availables = [entry["available"] for entry in data]
    # availability_ratio = availables / totals
    availability_ratios = [a / t for a, t in zip(availables, totals)]
    [print(availability_ratios)]
    # not_reachables = [entry["not_reachable"] for entry in data]
    return timestamps, availability_ratios


# Function to parse timestamp from filename
def parse_timestamp(filename):
    basename = os.path.basename(filename)
    # timestamp_str = re.search(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv", basename).group()[:-4]
    timestamp_str = re.search(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_cleaned\.csv", basename).group()[:-12]
    return datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

en_timestamps, en_availability_ratios = evaluate_data('en')
ru_timestamps, ru_availability_ratios = evaluate_data('ru')
uk_timestamps, uk_availability_ratios = evaluate_data('uk')
tr_timestamps, tr_availability_ratios = evaluate_data('tr')
ar_timestamps, ar_availability_ratios = evaluate_data('ar')
zh_timestamps, zh_availability_ratios = evaluate_data('zh')
my_timestamps, my_availability_ratios = evaluate_data('my')
fa_timestamps, fa_availability_ratios = evaluate_data('fa')

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(en_timestamps, en_availability_ratios, label="English", color='darkred')
plt.plot(ru_timestamps, ru_availability_ratios, label="Russian", color='darkblue')
plt.plot(uk_timestamps, uk_availability_ratios, label="Ukrainian", color='blue')
plt.plot(tr_timestamps, tr_availability_ratios, label="Turkish", color='red')
plt.plot(ar_timestamps, ar_availability_ratios, label="Arabian", color='yellow')
plt.plot(zh_timestamps, zh_availability_ratios, label="Chinese", color='black')
plt.plot(my_timestamps, my_availability_ratios, label="Burmese", color='teal')
plt.plot(fa_timestamps, fa_availability_ratios, label="Persian", color='orange')
# plt.plot(timestamps, reachables, label="Reachable", color='green')
# plt.plot(timestamps, not_reachables, label="Non-reachable", color='red')
plt.xlabel("Timestamp")
plt.ylabel("Percentage of articles that have at least one Provider")
plt.title("CID Availability over Time")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'availability_ratios_{sample_size}.png')
# plt.show()
