import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import csv

sample_percentage = float(sys.argv[1])
measurement_name = str(sys.argv[2])

wikipedia_file_suffix = '.wikipedia-on-ipfs.org_links_1_CID.csv'

def count_rows_in_csv(file_path):
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        
        # Skip the header
        next(csvreader)
        row_count = sum(1 for row in csvreader)
        # print(row_count)
    return row_count

def evaluate_data(language, sample_size):
    # Read CSV files and store their data in a list of dictionaries
    data = []
    # pattern = r"^[a-z]{2}\.wikipedia-on-ipfs\.org_links_1_CID_providers_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv$"
    pattern = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv$"
    for file in glob.glob(f"./data/{language}/{sample_size}_{measurement_name}/Providers/*.csv"):
        print(file)
        if re.match(pattern, os.path.basename(file)):
            # print(file)
            df = pd.read_csv(file)
            timestamp = parse_timestamp(file)
            total = len(df)
            reachable = len(df[df["Reachable"] == True])
            not_reachable = total - reachable
            data.append({"timestamp": timestamp, "total": total, "reachable": reachable, "not_reachable": not_reachable})
            print(data)

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

# print(count_rows_in_csv('en' + str(wikipedia_file_suffix)))
# print(int(count_rows_in_csv('en' + str(wikipedia_file_suffix)) * sample_percentage))

en_timestamps, en_reachables = evaluate_data('en', int(count_rows_in_csv('en' + str(wikipedia_file_suffix)) * sample_percentage))
ru_timestamps, ru_reachables = evaluate_data('ru', int(count_rows_in_csv('ru' + str(wikipedia_file_suffix)) * sample_percentage))
uk_timestamps, uk_reachables = evaluate_data('uk', int(count_rows_in_csv('uk' + str(wikipedia_file_suffix)) * sample_percentage))
tr_timestamps, tr_reachables = evaluate_data('tr', int(count_rows_in_csv('tr' + str(wikipedia_file_suffix)) * sample_percentage))
ar_timestamps, ar_reachables = evaluate_data('ar', int(count_rows_in_csv('ar' + str(wikipedia_file_suffix)) * sample_percentage))
zh_timestamps, zh_reachables = evaluate_data('zh', int(count_rows_in_csv('zh' + str(wikipedia_file_suffix)) * sample_percentage))
my_timestamps, my_reachables = evaluate_data('my', int(count_rows_in_csv('my' + str(wikipedia_file_suffix)) * sample_percentage))
fa_timestamps, fa_reachables = evaluate_data('fa', int(count_rows_in_csv('fa' + str(wikipedia_file_suffix)) * sample_percentage))

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(en_timestamps, en_reachables, label="English", color='darkred')
plt.plot(ru_timestamps, ru_reachables, label="Russian", color='darkblue')
plt.plot(uk_timestamps, uk_reachables, label="Ukrainian", color='blue')
plt.plot(tr_timestamps, tr_reachables, label="Turkish", color='red')
plt.plot(ar_timestamps, ar_reachables, label="Arabic", color='yellow')
plt.plot(zh_timestamps, zh_reachables, label="Chinese", color='black')
plt.plot(my_timestamps, my_reachables, label="Myanmar (Burmese)", color='teal')
plt.plot(fa_timestamps, fa_reachables, label="Persian (Farsi)", color='orange')
# plt.plot(timestamps, reachables, label="Reachable", color='green')
# plt.plot(timestamps, not_reachables, label="Non-reachable", color='red')

plt.xlabel("Timestamp")
plt.ylabel("Number of unique providers")
plt.title("Unique Providers per Language")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'figures/unique_reachable_providers_{sample_percentage}_{measurement_name}.png')
# plt.show()
