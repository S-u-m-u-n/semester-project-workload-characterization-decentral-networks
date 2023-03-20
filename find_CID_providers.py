import csv
import re
import subprocess
from collections import defaultdict
from tqdm import tqdm
import maxminddb

# Define the input and output CSV filenames
# input_filename = "./en.wikipedia-on-ipfs.org_CID.csv"
input_filename = "en.wikipedia-on-ipfs.org_CID copy.csv"
output1_filename = "output1.csv"
output2_filename = "output2.csv"

# Create a dictionary to keep track of the number of appearances of each provider ID
provider_counts = defaultdict(int)

# Define a function to check if a provider is reachable and extract its IP address and geolocation
def get_provider_information(provider):
    try:
        output = subprocess.check_output(f"ipfs dht findpeer {provider}", shell=True).decode()
    except:
        print(f'ipfs dht findpeer {provider} returned an error.')
        return False, None, None
    for line in output.splitlines():
        match = re.match(r"/ip4/(\d+\.\d+\.\d+\.\d+)/tcp/4001", line)
        if match:
            ip_address = match.group(1)
            # Load the GeoLite2 database
            db_filename = "<path to GeoLite2 database file>"
            with maxminddb.open_database(db_filename) as reader:
                # Look up the geolocation of the IP address in the GeoLite2 database
                try:
                    response = reader.get(ip_address)
                    if response:
                        location = f"{response.get('latitude', '')},{response.get('longitude', '')}"
                    else:
                        location = None
                except:
                    location = None
            return True, ip_address, location
    return False, None, None

# Define a function to process a single CID and return the corresponding row for output1.csv
def process_cid(cid):
    output = subprocess.check_output(f"ipfs dht findprovs {cid}", shell=True).decode().strip().split("\n")
    providers = [p.split("/")[-1] for p in output]
    for p in providers:
        provider_counts[p] += 1
    return [len(providers), ",".join(providers)]

# Open the input CSV file and create the output1 CSV file
with open(input_filename, "r") as input_file, open(output1_filename, "w", newline="") as output1_file:
    # Set up the CSV reader and writer objects
    input_reader = csv.reader(input_file)
    input_rows = list(input_reader)
    num_rows = len(input_rows) - 1 # Subtract 1 for the header row
    output1_writer = csv.writer(output1_file)
    # Write the header row for output1.csv
    output1_writer.writerow(["Original Link", "Resolved CID", "Number of Providers", "List of Providers"])
    # Loop over the input rows and process each CID
    for i, row in tqdm(enumerate(input_rows[1:]), total=num_rows):
        original_link, resolved_cid = row
        output1_row = [original_link, resolved_cid] + process_cid(resolved_cid)
        output1_writer.writerow(output1_row)

# Create the output2 CSV file
with open(output2_filename, "w", newline="") as output2_file:
    # Set up the CSV writer object
    output2_writer = csv.writer(output2_file)
    # Write the header row for output2.csv
    output2_writer.writerow(["Provider ID", "Number of Appearances", "Reachable", "IP Address", "Location"])
    # Loop over the provider counts and check each provider for reachability
    num_providers = len(provider_counts)
    for i, (provider, count) in tqdm(enumerate(provider_counts.items()), total=num_providers):
        reachable, ip_address, location = get_provider_information(provider)
        output2_row = [provider, count, reachable, ip_address, location]
        output2_writer.writerow(output2_row)
