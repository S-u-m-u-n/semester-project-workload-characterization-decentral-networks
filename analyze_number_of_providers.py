import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import csv
from matplotlib.ticker import MaxNLocator
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter

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

languages = [('en', 'English', 'darkred'),
            ('ru', 'Russian', 'darkblue'),
            ('uk', 'Ukrainian', 'blue'),
            ('tr', 'Turkish', 'red'),
            ('ar', 'Arabic', 'yellow'),
            ('zh', 'Chinese', 'black'),
            ('my', 'Myanmar (Burmese)', 'teal'),
            ('fa', 'Persian (Farsi)', 'orange')]

# Evaluate data and store results in two dictionaries
full_data = {}
sampled_data = {}
for lang, _, _ in languages:
    full_data[lang] = count_rows_in_csv(lang + str(wikipedia_file_suffix))
    sampled_data[lang] = evaluate_data(lang, int(count_rows_in_csv(lang + str(wikipedia_file_suffix)) * sample_percentage))

# Sort languages by the largest entries in full_data
sorted_languages = sorted(languages, key=lambda x: full_data[x[0]], reverse=True)

# Calculate the maximum width of the text labels
max_label_width = max([len(f"{full_data[lang],}") for lang, _, _ in sorted_languages])

# Create horizontal histogram plot using full_data and sorted_languages
# fig, ax = plt.subplots(figsize=(10, 6))
fig, ax = plt.subplots(figsize=(10 + max_label_width * 0.6, 8))
for i, (lang, _, color) in enumerate(sorted_languages):
    count = full_data[lang]  # Use the last value in the 'reachables' list
    ax.barh(i, count, color=color, alpha=0.7)
    ax.text(count + 10, i, f"{count:,}", ha='left', va='center', fontsize=12)
ax.set_yticks(range(len(sorted_languages)))
ax.set_yticklabels([name for _, name, _ in sorted_languages])
ax.invert_yaxis()
ax.set_xlabel('Number of Articles')
ax.set_title('Wikipedia Articles per Language')

# Set the x-axis to display only integers
ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

# Adjust the right margin to prevent numbers from going outside the plot
plt.subplots_adjust(right=0.95)

plt.tight_layout()
plt.savefig(f'figures/articles_per_language.png')
plt.clf()


# Plot the data
plt.figure(figsize=(10, 6))
for lang, label, color in languages:
    plt.plot(sampled_data[lang][0], sampled_data[lang][1], label=label, color=color)

plt.xlabel("Timestamp")
plt.ylabel("Number of Unique, Reachable Providers")
plt.title("Unique Providers")
plt.legend()
# plt.xticks(rotation=45)

# Set the y-axis to have only integer labels
ax = plt.gca()  # Get the current axis
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.xaxis.set_major_formatter(DateFormatter('%d.%m, %H:%M'))

plt.tight_layout()
plt.savefig(f'figures/unique_reachable_providers_{sample_percentage}_{measurement_name}.png')
# plt.show()
