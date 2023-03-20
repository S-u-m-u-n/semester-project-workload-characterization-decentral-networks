import argparse
import pandas as pd
import matplotlib.pyplot as plt

def convert_rate(value):
    num, unit = value.split()
    num = float(num)

    if unit == "B/s":
        return num
    elif unit == "kB/s":
        return num * 1e3
    elif unit == "MB/s":
        return num * 1e6
    else:
        raise ValueError(f"Unknown unit: {unit}")

def plot_rate(csv_file, avg_window=1):
    # Read the CSV file
    df = pd.read_csv(csv_file, parse_dates=["Timestamp"])

    # Convert RateIn and RateOut to numeric values in B/s
    df['RateIn'] = df['RateIn'].apply(convert_rate)
    df['RateOut'] = df['RateOut'].apply(convert_rate)

    # Set the index to the Timestamp column
    df.set_index("Timestamp", inplace=True)

    # Apply the moving average with the specified window size
    if avg_window > 1:
        df['RateIn'] = df['RateIn'].rolling(window=avg_window).mean()
        df['RateOut'] = df['RateOut'].rolling(window=avg_window).mean()

    # Convert the rates back to kB/s for plotting
    df['RateIn'] /= 1e3
    df['RateOut'] /= 1e3

    # Plot RateIn and RateOut over time
    fig, ax = plt.subplots()
    df[['RateIn', 'RateOut']].plot(ax=ax)
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Rate (kB/s)")
    ax.set_title("RateIn and RateOut Development over Time")
    plt.savefig('bandwidth_consumption.png')
    # plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot RateIn and RateOut from CSV file.")
    parser.add_argument("csv_file", help="Path to the CSV file")
    parser.add_argument("-a", "--average", type=int, default=1, help="Average consecutive values with the specified window size")
    args = parser.parse_args()

    plot_rate(args.csv_file, args.average)