import time
import argparse
import subprocess
import sys
import csv
import matplotlib.pyplot as plt

random_seed = 42
current_iteration = 0

languages = [('en', 1), ('tr', 1), ('my', 1), ('ar', 1), ('zh', 1), ('uk', 1), ('ru', 1), ('fa', 1)]

wikipedia_file_suffix = '.wikipedia-on-ipfs.org_links_1_CID.csv'

def count_rows_in_csv(file_path):
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        
        # Skip the header
        next(csvreader)
        row_count = sum(1 for row in csvreader)
        # print(row_count)
    return row_count

def run_script(filename, sample_size, random_seed):
    script_path = 'process_CID.py'
    # result = subprocess.run(["python", script_path, filename, sample_size, random_seed], check=True)
    result = subprocess.run(["python3", script_path, filename, str(sample_size), str(random_seed)], check=True)
    return result

def run_all_scripts(random_seed):
    for i in range(len(languages)):
        run_script('./' + str(languages[i][0]) + str(wikipedia_file_suffix), int(languages[i][1]), int(random_seed))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a script at fixed time intervals.")
    # parser.add_argument("script_path", help="Path to the script you want to run.")
    # parser.add_argument("sample_size", help="Number of articles to sample. 0 means everything.")
    parser.add_argument("sample_percentage", type=float, help="Percentage of articles to sample per language (0.xx).")
    parser.add_argument("interval", type=int, help="Interval in seconds between script runs.")

    args = parser.parse_args()

    sample_percentage = args.sample_percentage
    interval = args.interval

    for i in range(len(languages)):
        languages[i] = (languages[i][0], count_rows_in_csv(str(languages[i][0]) + str(wikipedia_file_suffix)))
    
    languages = sorted(languages, key=lambda x: x[1], reverse=True)
    print(languages)

    # Extract the values and labels from the languages list
    values = [x[1] for x in languages]
    labels = [x[0] for x in languages]

    # Set the figure size and font size
    plt.figure(figsize=(12, 6))
    plt.rcParams.update({'font.size': 12})


    # Create the histogram
    plt.bar(labels, values)

    # Set the labels and title of the histogram
    plt.xlabel('Languages')
    plt.ylabel('Number of Articles')
    plt.title('Number of Unique Articles per Wikipedia Language (with one level of recursion)')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=90)

    # plt.savefig('./figures/Wikipedia_number_of_articles_with_recursion_1.png')
    plt.savefig('./figures/Wikipedia_number_of_articles.png', bbox_inches='tight')

    for i in range(len(languages)):
        languages[i] = (languages[i][0], int(languages[i][1] * sample_percentage))

    print(languages)

    try:
        while True:
            start_time = time.time()
            run_all_scripts(int(random_seed + current_iteration))
            end_time = time.time()
            execution_time = end_time - start_time

            print(f"Iteration {current_iteration + 1} took {execution_time/60} minutes.")
            print(f"Waiting for {(interval - execution_time)/60} minutes before running the script again...")
            time.sleep(interval - execution_time)
            current_iteration += 1

    except KeyboardInterrupt:
        print("Script execution stopped manually.")
