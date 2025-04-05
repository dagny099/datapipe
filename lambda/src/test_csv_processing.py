import pandas as pd
from data_cleaning import clean_data

# Load a sample CSV file
sample_csv_path = '~/PROJECTS/user2632022_workout_history.csv'

print(f"Testing CSV processing with file: {sample_csv_path}")


# Read the CSV data using StringIO
df = pd.read_csv(sample_csv_path)
print(f"Original CSV data ({len(df)} rows):")
print(df.head())

# Apply the cleaning function
cleaned_df = clean_data(df)

print("\nCleaned DataFrame:")
print(cleaned_df)
