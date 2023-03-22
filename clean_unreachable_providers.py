import csv
import sys
import os
import glob

languages = ['en', 'ru', 'uk', 'tr', 'my', 'zh', 'fa', 'ar']

def load_csv_files(providers_csv, detailed_cid_csv):
    try:
        with open(providers_csv, 'r', newline='') as file_a_obj:
            unreachable_entries = []
            csv_reader_a = csv.reader(file_a_obj)
            _ = next(csv_reader_a)  # Skip the header row
            for row in csv_reader_a:
                reachable = row[2]
                if reachable.lower() == "false":
                    unreachable_entries.append(row[0])
            
            # print(unreachable_entries)

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
        with open(detailed_cid_csv[:-4] + '_cleaned.csv', 'w', newline='') as updated_file_obj:
            csv_writer = csv.writer(updated_file_obj)
            csv_writer.writerows(updated_rows)

    except FileNotFoundError:
        print(f"File '{detailed_cid_csv}' not found.")

def find_matching_files(language):
    folder = os.path.join('./data', str(language), str(sample_size))
    cid_path = os.path.join(folder, 'CID', '*.csv')
    provider_path = os.path.join(folder, 'Providers', '*.csv')

    cid_files = {os.path.basename(file): file for file in glob.glob(cid_path)}
    provider_files = {os.path.basename(file): file for file in glob.glob(provider_path)}

    matching_files = [(provider_files[file_name], cid_files[file_name]) for file_name in provider_files if file_name in cid_files]

    return matching_files

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the sample_size.")
    else:
        sample_size = int(sys.argv[1])

        for l in languages:
            # print(l)
            matching_file_pairs = find_matching_files(l)        
            if not matching_file_pairs:
                print(f"No matching file pairs found in {l}")
            else:
                for providers_csv, detailed_cid_csv in matching_file_pairs:
                    print(f"Processing files: '{providers_csv}' and '{detailed_cid_csv}'")
                    load_csv_files(providers_csv, detailed_cid_csv)
