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

# Get csv file path from command line argument
input_filename = str(sys.argv[1])
sample_size = int(sys.argv[2])
random_seed = int(sys.argv[3])
random.seed(random_seed)

now = datetime.datetime.now()
date_string = now.strftime('%Y-%m-%d_%H-%M-%S')

folder = f"./data/{input_filename[:4]}/{sample_size}"
folder_CID = f"./data/{input_filename[:4]}/{sample_size}/CID"
folder_Providers = f"./data/{input_filename[:4]}/{sample_size}/Providers"

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
    for attempt in range(max_attempts):
        result = process_cid(cid)
        if result != [0, ',']:
            return result
        # Wait for a random amount of time between 1 and 4 seconds before trying again
        sleep_time = random.uniform(1, 4)
        time.sleep(sleep_time)
    print(f"Couldn't find any providers for {cid}")
    return [0, ',']

def process_cid(cid):
    try:
        result = subprocess.run(f"ipfs dht findprovs {cid}", shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip().split("\n")
    except subprocess.TimeoutExpired as e:
        if e.stdout is not None:
            output = e.stdout.decode().strip().split("\n")
        else:
            return [0, ',']
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}: {e.output}")
        print(f"Error on: ipfs dht findprovs {cid}")
        return [0, ',']

    filtered_output = [item for item in output if item]
    if not filtered_output:
        return [0, ',']

    providers = [p.split("/")[-1] for p in filtered_output]
    for p in providers:
        provider_counts[p] += 1
    return [len(providers), ",".join(providers)]


def process_row(row):
    original_link, resolved_cid = row
    output1_row = [original_link, resolved_cid] + process_cid_with_retry(resolved_cid)
    # output1_row = [original_link, resolved_cid] + process_cid(resolved_cid)
    return output1_row

# Open the input CSV file and create the output1 CSV file
with open(input_filename, "r") as input_file, open(output1_filename, "w", newline="") as output1_file:
    # Set up the CSV reader and writer objects
    input_reader = csv.reader(input_file)
    input_rows = list(input_reader)[1:]
    if sample_size == 0:
        num_rows = len(input_rows)
    else:
        num_rows = int(sample_size)
        input_rows = random.sample(input_rows, num_rows)
    output1_writer = csv.writer(output1_file)
    # Write the header row for output1.csv
    output1_writer.writerow(["Original Link", "Resolved CID", "Number of Providers", "List of Providers"])

    # Process CIDs in parallel
    with ThreadPoolExecutor(max_workers=128) as executor:
        output_rows = list(tqdm(executor.map(process_row, input_rows), total=num_rows))

    # Write the processed rows to output1.csv
    output1_writer.writerows(output_rows)

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
