import csv
import datetime
import sys

def validate_timestamp(timestamp):
    try:
        datetime.datetime.strptime(timestamp, "%Y-%m-%d_%H-%M-%S")
        return True
    except ValueError:
        return False

def load_csv_files(timestamp):
    if not validate_timestamp(timestamp):
        print("Invalid timestamp format. Please use 'YYYY-MM-DD_hh-mm-ss'.")
        return

    providers_csv = f'./data/en.wikipedia-on-ipfs.org_CID_providers_{timestamp}.csv'
    detailed_cid_csv = f'./data/en.wikipedia-on-ipfs.org_CID_detailed_{timestamp}.csv'

    try:
        with open(providers_csv, 'r', newline='') as file_a_obj:
            unreachable_entries = []
            csv_reader_a = csv.reader(file_a_obj)
            _ = next(csv_reader_a)  # Skip the header row
            for row in csv_reader_a:
                reachable = row[2]
                if reachable.lower() == "false":
                    unreachable_entries.append(row[0])
            
            print(unreachable_entries)

    except FileNotFoundError:
        print(f"File '{providers_csv}' not found.")

    try:
        updated_rows = []
        with open(detailed_cid_csv, 'r', newline='') as file_b_obj:
            csv_reader_b = csv.reader(file_b_obj)
            headers = next(csv_reader_b)  # Skip the header row
            updated_rows.append(headers)

            for row in csv_reader_b:
                provider_list = row[3].split(',')
                reachable_providers = [p for p in provider_list if p not in unreachable_entries]
                row[3] = ','.join(reachable_providers)
                row[2] = len(reachable_providers)
                updated_rows.append(row)

        # Write the updated rows to a new CSV file
        with open(detailed_cid_csv + 'cleaned.csv', 'w', newline='') as updated_file_obj:
            csv_writer = csv.writer(updated_file_obj)
            csv_writer.writerows(updated_rows)

    except FileNotFoundError:
        print(f"File '{detailed_cid_csv}' not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a timestamp in the format 'YYYY-MM-DD_hh_mm_ss'.")
    else:
        timestamp = sys.argv[1]
        load_csv_files(timestamp)