import time
import argparse
import subprocess

def run_script(script_path, filename):
    result = subprocess.run(["python", script_path, filename], check=True)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a script at fixed time intervals.")
    parser.add_argument("script_path", help="Path to the script you want to run.")
    parser.add_argument("filename", help="File that the script should process.")
    parser.add_argument("interval", type=int, help="Interval in seconds between script runs.")

    args = parser.parse_args()

    script_path = args.script_path
    filename = args.filename
    interval = args.interval

    try:
        while True:
            run_script(script_path, filename)

            print(f"Waiting for {interval/60} minutes before running the script again...")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("Script execution stopped manually.")
