import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import csv
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator

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
    pattern = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_cleaned\.csv$"
    # pattern = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv$"
    for file in glob.glob(f"./data/{language}/{sample_size}_{measurement_name}/CID/*.csv"):
        # print(file)
        if re.match(pattern, os.path.basename(file)):
            # print(file)
            df = pd.read_csv(file)
            timestamp = parse_timestamp(file)
            total = len(df)
            availables = len(df[df["Number of Providers"] > 0])
            # unavailables = total - availables
            # print(availables)
            # print(df[df["Number of Providers"] > 0])

            availability_ratio = availables / total
            # print(availability_ratio)
            data.append({"timestamp": timestamp, "availability_ratio": availability_ratio})
            if availability_ratio == 0:
                print(file)

    # Sort the data by timestamp
    data.sort(key=lambda x: x["timestamp"])

    # Extract data for plotting
    timestamps = [entry["timestamp"] for entry in data]
    # print(timestamps)
    # totals = [entry["total"] for entry in data]
    availability_ratio = [entry["availability_ratio"] for entry in data]
    # not_reachables = [entry["not_reachable"] for entry in data]
    return timestamps, availability_ratio

# Function to parse timestamp from filename
def parse_timestamp(filename):
    basename = os.path.basename(filename)
    timestamp_str = re.search(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", basename).group()
    # print(timestamp_str)
    return datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

languages = [('en', 'English', 'darkred'),
            ('ru', 'Russian', 'darkblue'),
            ('uk', 'Ukrainian', 'blue'),
            ('tr', 'Turkish', 'red'),
            ('ar', 'Arabic', 'yellow'),
            ('zh', 'Chinese', 'black'),
            ('my', 'Myanmar (Burmese)', 'teal'),
            ('fa', 'Persian (Farsi)', 'orange')]

# Evaluate data and store results in two dictionaries
sampled_data = {}
for lang, _, _ in languages:
    sampled_data[lang] = evaluate_data(lang, int(count_rows_in_csv(lang + str(wikipedia_file_suffix)) * sample_percentage))

# Plot the data
plt.figure(figsize=(10, 6))
for lang, label, color in languages:
    plt.plot(sampled_data[lang][0], sampled_data[lang][1], label=label, color=color)

plt.xlabel("Timestamp")
plt.ylabel("Article Availability Ratio")
plt.title("Article Availability")
plt.legend()
# plt.xticks(rotation=45)

ax = plt.gca()  # Get the current axis
ax.xaxis.set_major_formatter(DateFormatter('%d.%m, %H:%M'))

# Set the y-axis to have only integer labels
# ax.yaxis.set_major_locator(MaxNLocator(integer=True))
# ax.yaxis.set_major_locator(MultipleLocator(0.1))

plt.tight_layout()
plt.savefig(f'figures/article_availability_ratio_{sample_percentage}_{measurement_name}.png')
# plt.show()
