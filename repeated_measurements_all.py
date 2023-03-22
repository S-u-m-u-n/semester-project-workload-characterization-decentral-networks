import time
import argparse
import subprocess

def run_script(script_path, filename):
    result = subprocess.run(["python", script_path, filename], check=True)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a script at fixed time intervals.")
    parser.add_argument("script_path", help="Path to the script you want to run.")
    parser.add_argument("interval", type=int, help="Interval in seconds between script runs.")

    args = parser.parse_args()

    script_path = args.script_path
    interval = args.interval

    try:
        while True:
            run_script(script_path, './en.wikipedia-on-ipfs.org_links_1.txt_CID.csv')
            run_script(script_path, './tr.wikipedia-on-ipfs.org_links_1.txt_CID.csv')
            run_script(script_path, './my.wikipedia-on-ipfs.org_links_1.txt_CID.csv')
            run_script(script_path, './ar.wikipedia-on-ipfs.org_links_1.txt_CID.csv')
            run_script(script_path, './zh.wikipedia-on-ipfs.org_links_1.txt_CID.csv')
            run_script(script_path, './uk.wikipedia-on-ipfs.org_links_1.txt_CID.csv')
            run_script(script_path, './ru.wikipedia-on-ipfs.org_links_1.txt_CID.csv')
            run_script(script_path, './fa.wikipedia-on-ipfs.org_links_1.txt_CID.csv')

            print(f"Waiting for {interval/60} minutes before running the script again...")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("Script execution stopped manually.")
