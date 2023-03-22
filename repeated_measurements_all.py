import time
import argparse
import subprocess
import sys

def run_script(script_path, filename, sample_size):
    result = subprocess.run(["python", script_path, filename, sample_size], check=True)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a script at fixed time intervals.")
    parser.add_argument("script_path", help="Path to the script you want to run.")
    parser.add_argument("sample_size", help="Number of articles to sample. 0 means everything.")
    parser.add_argument("interval", type=int, help="Interval in seconds between script runs.")

    args = parser.parse_args()

    script_path = args.script_path
    sample_size = args.sample_size
    interval = args.interval

    try:
        while True:
            start_time = time.time()
            run_script(script_path, './en.wikipedia-on-ipfs.org_links_1_CID.csv', sample_size)
            run_script(script_path, './tr.wikipedia-on-ipfs.org_links_1_CID.csv', sample_size)
            run_script(script_path, './my.wikipedia-on-ipfs.org_links_1_CID.csv', sample_size)
            run_script(script_path, './ar.wikipedia-on-ipfs.org_links_1_CID.csv', sample_size)
            run_script(script_path, './zh.wikipedia-on-ipfs.org_links_1_CID.csv', sample_size)
            run_script(script_path, './uk.wikipedia-on-ipfs.org_links_1_CID.csv', sample_size)
            run_script(script_path, './ru.wikipedia-on-ipfs.org_links_1_CID.csv', sample_size)
            run_script(script_path, './fa.wikipedia-on-ipfs.org_links_1_CID.csv', sample_size)
            end_time = time.time()
            execution_time = end_time - start_time

            print(f"Execution took {execution_time/60} minutes.")
            print(f"Waiting for {(interval - execution_time)/60} minutes before running the script again...")
            time.sleep(interval - execution_time)

    except KeyboardInterrupt:
        print("Script execution stopped manually.")
