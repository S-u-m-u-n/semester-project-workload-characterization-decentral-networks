import csv
import re
import subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import sys
import random
import os
from tqdm import tqdm
import datetime
import time
from threading import Lock

unavailable_articles_lock = Lock()

# Get csv file path from command line argument
input_filename = str(sys.argv[1])
sample_size = int(sys.argv[2])
measurement_name = str(sys.argv[3])
random_seed = int(sys.argv[4])
random.seed(random_seed)

# Get the additional input_rows list from the command line argument
# additional_rows = []
# if len(sys.argv) > 4:
    # additional_rows = eval(sys.argv[4])

now = datetime.datetime.now()
date_string = now.strftime('%Y-%m-%d_%H-%M-%S')

folder = f"./data/{input_filename[:4]}/{sample_size}_{measurement_name}"
folder_CID = f"{folder}/CID"
folder_Providers = f"{folder}/Providers"

if not os.path.exists(folder):
    os.mkdir(folder)

if not os.path.exists(folder_CID):
    os.mkdir(folder_CID)

if not os.path.exists(folder_Providers):
    os.mkdir(folder_Providers)

output1_filename = f"{folder_CID}/{date_string}.csv"
output2_filename = f"{folder_Providers}/{date_string}.csv"

# Create a dictionary to keep track of the number of appearances of each provider ID
provider_counts = defaultdict(int)


# # Create a list to keep track of the rows that returned [0, ''] in process_cid_with_retry
# zero_provider_rows = []

# # Load zero_provider_rows from the latest file if present
# def load_zero_provider_rows(folder_CID):
#     zero_provider_rows_files = glob.glob(f"{folder_CID}/zero_provider_rows_*.txt")
#     if zero_provider_rows_files:
#         latest_zero_provider_rows_file = max(zero_provider_rows_files, key=os.path.getctime)
#         if os.path.getsize(latest_zero_provider_rows_file) == 0:
#             return []
#         else:
#             with open(latest_zero_provider_rows_file, "r") as f:
#                 zero_provider_rows_data = [int(x) for x in f.read().split(",")]
#             return zero_provider_rows_data
#     else:
#         return []


def get_provider_information(provider, max_attempts=2):
    output = ''
    for attempt in range(max_attempts):
        try:
            output = subprocess.check_output(f"ipfs dht findpeer {provider}", shell=True, timeout=10, stderr=subprocess.DEVNULL).decode()
        except subprocess.TimeoutExpired as e:
            if e.stdout is not None:
                print(e.stdout)
            return False, None
        except:
            return False, None

        for line in output.splitlines():
            match = re.match(r"/ip4/((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))/tcp", line)
            if match:
                ip_address = match.group(1)
                if ip_address not in ('127.0.0.1', '0.0.0.0'):
                    return True, ip_address

    print(provider + ' no suitable connection possible')
    print(output)
    return False, None

def process_cid_with_retry(cid, max_attempts=2):
    global unavailable_articles
    for attempt in range(max_attempts):
        result = process_cid(cid)
        if result != [0, '']:
            return result
        sleep_time = random.uniform(1, 4)
        time.sleep(sleep_time)
    with unavailable_articles_lock:  # Acquire the lock before updating the variable
        unavailable_articles += 1
    return [0, '']

def process_cid(cid):
    try:
        # ulimit = 'ulimit -v 64000; '
        result = subprocess.run(f"ipfs dht findprovs {cid}", shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip().split("\n")
    except subprocess.TimeoutExpired as e:
        if e.stdout is not None:
            output = e.stdout.decode().strip().split("\n")
        else:
            return [0, '']
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}: {e.output}")
        print(f"Error on: ipfs dht findprovs {cid}")
        return [0, '']

    filtered_output = [item for item in output if item]
    if not filtered_output:
        return [0, '']

    providers = [p.split("/")[-1] for p in filtered_output]
    for p in providers:
        provider_counts[p] += 1
    return [len(providers), ",".join(providers)]

def process_row(row):
    original_link, resolved_cid = row
    output1_row = [original_link, resolved_cid] + process_cid_with_retry(resolved_cid)
    # output1_row = [original_link, resolved_cid] + process_cid(resolved_cid)
    return output1_row

def remove_duplicate_rows(input_rows, additional_rows):
    additional_rows_set = set(tuple(row) for row in additional_rows)
    unique_input_rows = [row for row in input_rows if tuple(row) not in additional_rows_set]
    return unique_input_rows

# Open the input CSV file and create the output1 CSV file
with open(input_filename, "r") as input_file, open(output1_filename, "w", newline="") as output1_file:
    # Set up the CSV reader and writer objects
    input_reader = csv.reader(input_file)
    input_rows = list(input_reader)[1:]
    num_total_rows = len(input_rows)
    if sample_size == 0:
        num_rows = num_total_rows
    else:
        num_rows = int(sample_size)
        input_rows = random.sample(input_rows, num_rows)

    unavailable_articles = 0

    # else:
    #     # Sample row indices and exclude additional row indices from the sample
    #     additional_row_indices = set(load_zero_provider_rows(folder_CID))
    #     available_row_indices = set(range(num_total_rows)) - additional_row_indices
    #     sampled_row_indices = random.sample(available_row_indices, min(sample_size, len(available_row_indices)))
    #     input_row_indices = list(sampled_row_indices) + list(additional_row_indices)
        
    #     input_row_indices_to_original = {i: original_idx for i, original_idx in enumerate(input_row_indices)}
        
    #     input_rows = [input_rows[index] for index in input_row_indices]
    #     num_rows = len(input_rows)


    output1_writer = csv.writer(output1_file)
    # Write the header row for output1.csv
    output1_writer.writerow(["Original Link", "Resolved CID", "Number of Providers", "List of Providers"])

    # Process CIDs in parallel
    with ThreadPoolExecutor(max_workers=128) as executor:
        output_rows = list(tqdm(executor.map(process_row, input_rows), total=num_rows))

    # Extract the processed rows and zero_provider_rows from the output
    # zero_provider_rows = [index for index, row in output_rows_with_indices if row[-2:] == [0, '']]
    # zero_provider_rows = [input_row_indices_to_original[index] for index, row in output_rows_with_indices if row[-2:] == [0, '']]
    # output_rows = [row for index, row in output_rows_with_indices]

    # Write the processed rows to output1.csv
    output1_writer.writerows(output_rows)

### Print the rows that returned [0, ''] in process_cid_with_retry
# print(f"{len(zero_provider_rows)} out of {num_rows} rows had zero providers...")

print(f"{unavailable_articles} out of {num_rows} rows had no providers...")


### Save the zero_provider_rows to a file
# zero_provider_rows_filename = f"{folder_CID}/zero_provider_rows_{date_string}.txt"

# with open(zero_provider_rows_filename, "w") as zero_provider_rows_file:
    # zero_provider_rows_file.write(",".join(str(index) for index in zero_provider_rows))

# print(f"zero_provider_rows saved to {folder_CID}/zero_provider_rows_{date_string}.txt")

# Create the output2 CSV file
with open(output2_filename, "w", newline="") as output2_file:
    # Set up the CSV writer object
    output2_writer = csv.writer(output2_file)
    # Write the header row for output2.csv
    output2_writer.writerow(["Provider ID", "Number of Appearances", "Reachable", "IP Address"])

    # Process provider information in parallel
    with ThreadPoolExecutor(max_workers=64) as executor:
        output2_rows = list(tqdm(executor.map(get_provider_information, provider_counts.keys()), total=len(provider_counts)))

    # Write the processed provider information to output2.csv
    for (provider, count), (reachable, ip_address) in zip(provider_counts.items(), output2_rows):
        output2_row = [provider, count, reachable, ip_address]
        output2_writer.writerow(output2_row)
