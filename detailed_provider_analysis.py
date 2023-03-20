import argparse
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import subprocess

def get_country(ip_address):
    result = subprocess.run(["geoiplookup", ip_address], capture_output=True, text=True)
    output = result.stdout
    try:
        country = output.split(": ")[1].split(", ")[1]
        return country
    except:
        print(ip_address)
        # print(output)
        return ''


def analyze_csv(csv_file):
    # Read the CSV file and filter reachable rows
    df = pd.read_csv(csv_file)
    df = df[df["Reachable"]]

    # Histogram of the Number of Appearances
    plt.hist(df["Number of Appearances"], bins='auto')
    plt.xlabel("Number of Appearances")
    plt.ylabel("Frequency")
    plt.title("Histogram of Number of Appearances")
    plt.savefig('providers_number_of_appearances.png')
    # plt.show()

    # # Get the country for each IP address and count occurrences
    # df["Country"] = df["IP Address"].apply(get_country)
    # country_counts = df["Country"].value_counts()

    # # Load the world shapefile and merge with the country counts
    # world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    # world = world.merge(country_counts.rename("Counts"), left_on="name", right_index=True, how="left")
    # world["Counts"] = world["Counts"].fillna(0)

    # # Plot the world map with countries colored by occurrences
    # ax = world.plot(column="Counts", cmap="viridis", figsize=(15, 10), legend=True, scheme="quantiles", k=5, edgecolor="black", linewidth=0.2)
    # ax.set_title("Number of Appearances by Country")
    # plt.savefig('providers_geographical.png')
    # # plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze CSV and create histogram and world map.")
    parser.add_argument("csv_file", help="Path to the CSV file")
    args = parser.parse_args()

    analyze_csv(args.csv_file)