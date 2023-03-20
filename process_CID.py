import csv
import re
import subprocess
from collections import defaultdict
from tqdm import tqdm
import sys
# from geoip import geolite2
from concurrent.futures import ThreadPoolExecutor

# Get csv file path from command line argument
input_filename = sys.argv[1]

# Define the input and output CSV filenames
# input_filename = "./en.wikipedia-on-ipfs.org_CID.csv"
# input_filename = "en.wikipedia-on-ipfs.org_CID copy.csv"
# output1_filename = "output1.csv"
# output2_filename = "output2.csv"
import datetime

now = datetime.datetime.now()
date_string = now.strftime('%Y-%m-%d_%H-%M-%S')
# print(date_string)


output1_filename = f"./data/{input_filename.replace('_CID.csv', '')}_CID_detailed_{date_string}.csv"
output2_filename = f"./data/{input_filename.replace('_CID.csv', '')}_CID_providers_{date_string}.csv"

# Create a dictionary to keep track of the number of appearances of each provider ID
provider_counts = defaultdict(int)

# Define a function to check if a provider is reachable and extract its IP address and geolocation
def get_provider_information(provider):
    # print(provider)
    # output = ''
    try:
        output = subprocess.check_output(f"ipfs dht findpeer {provider}", shell=True, stderr=subprocess.DEVNULL).decode()
        # Run the command and suppress output
        # with open(subprocess.DEVNULL, 'w') as devnull:
            # output = subprocess.check_output(f"ipfs dht findpeer {provider}", shell=True, stderr=devnull).decode()

    except:
        # print(f'ipfs dht findpeer {provider} returned an error.')
        return False, None

    for line in output.splitlines():
        # match = re.match(r"/ip4/(\d+\.\d+\.\d+\.\d+)/tcp/4001", line)
        match = re.match(r"/ip4/(\d+\.\d+\.\d+\.\d+)/tcp/([0-9]|[1-9][0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])", line)
        
        if match:
            ip_address = match.group(1)
            # print(ip_address)
            # match = geolite2.lookup(ip_address).country
            # location = match.country
            # print(location)
            return True, ip_address
    print(provider + ' no suitable connection possible')
    return False, None

# Define a function to process a single CID and return the corresponding row for output1.csv
def process_cid(cid):
    # print(cid)
    try:
        result = subprocess.run(f"ipfs dht findprovs {cid}", shell=True, capture_output=True, text=True, timeout=20)
        output = result.stdout.strip().split("\n")
    except subprocess.TimeoutExpired as e:
        # print(f"Command timed out after {e.timeout} seconds.")
        output = e.stdout.decode().strip().split("\n")
        # print(output)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}: {e.output}")
        # print(cid)
        print(f'Error on: ipfs dht findprovs {cid}')
        return [0, ',']
    # output = subprocess.check_output(f"ipfs dht findprovs {cid}", shell=True).decode().strip().split("\n")
    providers = [p.split("/")[-1] for p in output]
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
    input_rows = list(input_reader)
    num_rows = len(input_rows) - 1 # Subtract 1 for the header row
    output1_writer = csv.writer(output1_file)
    # Write the header row for output1.csv
    output1_writer.writerow(["Original Link", "Resolved CID", "Number of Providers", "List of Providers"])

    # Process CIDs in parallel
    with ThreadPoolExecutor() as executor:
        output_rows = list(tqdm(executor.map(process_row, input_rows[1:]), total=num_rows))

    # Write the processed rows to output1.csv
    output1_writer.writerows(output_rows)

# Create the output2 CSV file
with open(output2_filename, "w", newline="") as output2_file:
    # Set up the CSV writer object
    output2_writer = csv.writer(output2_file)
    # Write the header row for output2.csv
    output2_writer.writerow(["Provider ID", "Number of Appearances", "Reachable", "IP Address"])

    # Process provider information in parallel
    with ThreadPoolExecutor() as executor:
        output2_rows = list(tqdm(executor.map(get_provider_information, provider_counts.keys()), total=len(provider_counts)))

    # Write the processed provider information to output2.csv
    for (provider, count), (reachable, ip_address) in zip(provider_counts.items(), output2_rows):
        output2_row = [provider, count, reachable, ip_address]
        output2_writer.writerow(output2_row)
