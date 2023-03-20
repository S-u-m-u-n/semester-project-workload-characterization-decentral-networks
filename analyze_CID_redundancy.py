import sys
import csv
import matplotlib.pyplot as plt
import numpy as np

def create_histogram(csv_file):
    number_of_providers = []

    with open(csv_file, 'r', newline='') as file_obj:
        csv_reader = csv.reader(file_obj)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            number_of_providers.append(int(row[2]))

    # Determine the range and appropriate bin size
    max_providers = max(number_of_providers)
    min_providers = min(number_of_providers)
    bin_size = 1
    bins = np.arange(min_providers - 0.5, max_providers + 0.5 + bin_size, bin_size)


    # Create a histogram
    plt.hist(number_of_providers, bins=bins, edgecolor='black', alpha=0.7)
    plt.xlabel('Number of Providers per Article')
    plt.ylabel('Articles')
    plt.title('Histogram of Number of Providers')

    # Show the plot
    plt.savefig('CID_availability.png')
    # plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_CID_redundancy.py <csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]
    create_histogram(csv_file)
