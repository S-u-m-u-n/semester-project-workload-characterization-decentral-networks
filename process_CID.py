import csv
import re
import subprocess
from collections import defaultdict
from tqdm import tqdm
import sys
import random
import os
# from geoip import geolite2
from concurrent.futures import ThreadPoolExecutor

# Get csv file path from command line argument
input_filename = str(sys.argv[1])
sample_size = int(sys.argv[2])
random_seed = int(sys.argv[3])
random.seed(random_seed)

# Define the input and output CSV filenames
# input_filename = "./en.wikipedia-on-ipfs.org_CID.csv"
# input_filename = "en.wikipedia-on-ipfs.org_CID copy.csv"
# output1_filename = "output1.csv"
# output2_filename = "output2.csv"
import datetime

now = datetime.datetime.now()
date_string = now.strftime('%Y-%m-%d_%H-%M-%S')
# print(date_string)

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

# Define a function to check if a provider is reachable and extract its IP address and geolocation
def get_provider_information(provider, max_attempts = 2):
    # print(provider)
    output = ''
    for attempt in range(max_attempts):
        try:
            output = subprocess.check_output(f"ipfs dht findpeer {provider}", shell=True, stderr=subprocess.DEVNULL).decode()
        except:
            return False, None

        for line in output.splitlines():
            # match = re.match(r"/ip4/(\d+\.\d+\.\d+\.\d+)/tcp/4001", line)
            match = re.match(r"/ip4/((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))/tcp", line)
            if match:
                ip_address = match.group(1)
                if ip_address not in ('127.0.0.1', '0.0.0.0'):
                    return True, ip_address
                # else:
                    # print("Weird IP")
                    # print(ip_address)
            # else:
                # print(line)
                # print("No match.")
                # return False, None
            
            # if match:
                # ip_address = match.group(1)
                # print(ip_address)
                # match = geolite2.lookup(ip_address).country
                # location = match.country
                # print(location)
                # return True, ip_address
    print(provider + ' no suitable connection possible')
    print(output)
    return False, None

# Define a function to process a single CID and return the corresponding row for output1.csv
def process_cid(cid):
    # print(cid)
    try:
        result = subprocess.run(f"ipfs dht findprovs {cid}", shell=True, capture_output=True, text=True, timeout=20)
        output = result.stdout.strip().split("\n")
    except subprocess.TimeoutExpired as e:
        # print(f"Command timed out after {e.timeout} seconds.")
        if e.stdout is not None:
            output = e.stdout.decode().strip().split("\n")
        else:
            print(f'Couldn\'t find any providers for {cid} ... Timeout')
            return [0, ',']
        # print(output)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}: {e.output}")
        # print(cid)
        print(f'Error on: ipfs dht findprovs {cid}')
        return [0, ',']
    # output = subprocess.check_output(f"ipfs dht findprovs {cid}", shell=True).decode().strip().split("\n")
    filtered_output = [item for item in output if item] # remove empty strings
    if filtered_output == []:
        print(f'Couldn\'t find any providers for {cid}')
        return [0, ',']

    providers = [p.split("/")[-1] for p in filtered_output]
    for p in providers:
        provider_counts[p] += 1
    return [len(providers), ",".join(providers)]

def process_row(row):
    original_link, resolved_cid = row
    output1_row = [original_link, resolved_cid] + process_cid(resolved_cid)
    return output1_row

# Open the input CSV file and create the output1 CSV file
with open(input_filename, "r") as input_file, open(output1_filename, "w", newline="") as output1_file:
    # Set up the CSV reader and writer objects
    input_reader = csv.reader(input_file)
    input_rows = list(input_reader)[1:]
    if sample_size == 0:
        num_rows = len(input_rows)
        # print(num_rows)
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
