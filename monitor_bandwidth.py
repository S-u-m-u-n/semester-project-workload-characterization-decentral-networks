import time
import argparse
import subprocess
import csv
from datetime import datetime

def run_ipfs_stats_bw():
    result = subprocess.run(["ipfs", "stats", "bw"], capture_output=True, text=True, check=True)
    return result.stdout

def parse_ipfs_stats_output(output):
    lines = output.strip().split('\n')[1:]
    stats = {}
    for line in lines:
        key, value = line.split(':')
        stats[key.strip()] = value.strip()
    return stats

def save_to_csv(writer, stats):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    stats['Timestamp'] = current_time
    writer.writerow(stats)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run 'ipfs stats bw' at specified time intervals and save the data to a CSV file.")
    parser.add_argument("interval", type=int, help="Interval in seconds between command runs.")
    parser.add_argument("csv_file", help="Path to the CSV file where the data will be saved.")

    args = parser.parse_args()

    interval = args.interval
    csv_file = args.csv_file

    try:
        with open(csv_file, 'w', newline='') as csvfile:
            fieldnames = ['Timestamp', 'TotalIn', 'TotalOut', 'RateIn', 'RateOut']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            try:
                while True:
                    output = run_ipfs_stats_bw()
                    stats = parse_ipfs_stats_output(output)
                    save_to_csv(writer, stats)

                    time.sleep(interval)

            except KeyboardInterrupt:
                print("Script execution stopped manually.")

    except IOError as e:
        print(f"Error while writing to CSV file: {e}")