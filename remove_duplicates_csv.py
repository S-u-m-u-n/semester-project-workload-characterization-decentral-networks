import pandas as pd
import sys

input_filename = sys.argv[1]


# read the CSV file into a DataFrame
df = pd.read_csv(input_filename)

# drop duplicate rows
df.drop_duplicates(inplace=True)

# write the DataFrame to a new CSV file
df.to_csv(input_filename, index=False)