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
    pattern = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv$"
    for file in glob.glob("./data/" + str(language) + "/" + str(sample_size) + "/Providers/*.csv"):
        # print(file)
        if re.match(pattern, os.path.basename(file)):
            # print(file)
            df = pd.read_csv(file)
            timestamp = parse_timestamp(file)
            total = len(df)
            reachable = len(df[df["Reachable"] == True])
            not_reachable = total - reachable
            data.append({"timestamp": timestamp, "total": total, "reachable": reachable, "not_reachable": not_reachable})
            # print(data)


    # Sort the data by timestamp
    data.sort(key=lambda x: x["timestamp"])

    # Extract data for plotting
    timestamps = [entry["timestamp"] for entry in data]
    # print(timestamps)
    # totals = [entry["total"] for entry in data]
    reachables = [entry["reachable"] for entry in data]
    # print(reachables)
    # not_reachables = [entry["not_reachable"] for entry in data]
    return timestamps, reachables


# Function to parse timestamp from filename
def parse_timestamp(filename):
    basename = os.path.basename(filename)
    timestamp_str = re.search(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv", basename).group()[:-4]
    return datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

en_timestamps, en_reachables = evaluate_data('en')
ru_timestamps, ru_reachables = evaluate_data('ru')
uk_timestamps, uk_reachables = evaluate_data('uk')
tr_timestamps, tr_reachables = evaluate_data('tr')
ar_timestamps, ar_reachables = evaluate_data('ar')
zh_timestamps, zh_reachables = evaluate_data('zh')
my_timestamps, my_reachables = evaluate_data('my')
fa_timestamps, fa_reachables = evaluate_data('fa')

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(en_timestamps, en_reachables, label="English", color='darkred')
plt.plot(ru_timestamps, ru_reachables, label="Russian", color='darkblue')
plt.plot(uk_timestamps, uk_reachables, label="Ukrainian", color='blue')
plt.plot(tr_timestamps, tr_reachables, label="Turkish", color='red')
plt.plot(ar_timestamps, ar_reachables, label="Arabian", color='yellow')
plt.plot(zh_timestamps, zh_reachables, label="Chinese", color='black')
plt.plot(my_timestamps, my_reachables, label="Burmese", color='teal')
plt.plot(fa_timestamps, fa_reachables, label="Persian", color='orange')
# plt.plot(timestamps, reachables, label="Reachable", color='green')
# plt.plot(timestamps, not_reachables, label="Non-reachable", color='red')
plt.xlabel("Timestamp")
plt.ylabel("Number of unique providers per language")
plt.title("Development of providers over time")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'unique_reachable_providers_{sample_size}.png')
# plt.show()
