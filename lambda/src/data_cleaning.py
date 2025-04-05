import pandas as pd
import numpy as np
import re
from datetime import datetime

# Custom date parsing function
def parse_date(date_string):
    """Function to parse date strings in various formats"""
    date_formats = [
        '%b. %d, %Y',  # Aug. 1, 2024
        '%d-%b-%y',    # 31-Jul-24
        '%d-%b-%Y',    # 31-Jul-2024
        '%B %d, %Y',   # July 31, 2024
        '%d-%m-%y',    # 20-06-23
        '%Y-%m-%d'     # 2024-08-01 (in case you have any in this format)
    ]   
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass    
    return None


# Function to clean data
def clean_data(df):
    """
    Function to clean data including:
        - drop unnecessary columns, 
        - drop rows with zero workout time, 
        - replace NaN values with None, 
        - date parsing for "Workout Date", and
        - rename columns to be more descriptive of units
    """

    initial_row_count = len(df)
    
    # Drop rows where 'Workout Time (seconds)' is 0 and create an explicit copy
    df = df[df['Workout Time (seconds)'] != 0].copy()
    rows_dropped = initial_row_count - len(df)   
    # print(f"Dropped {rows_dropped} rows with zero workout time.") ** ADD TO A REPORT **

    # Replace 'nan' with None for numeric columns
    numeric_columns = ['Calories Burned (kcal)', 'Distance (mi)', 'Workout Time (seconds)', 
                       'Avg Pace (min/mi)', 'Max Pace (min/mi)', 'Steps']
    for col in numeric_columns:
        df.loc[df[col].isna(), col] = None
    
    # Replace empty strings with None for string columns
    string_columns = ['Activity Type', 'Link']
    for col in string_columns:
        df.loc[df[col] == '', col] = None

    # Custom date parsing
    date_formats, invalid_dates  = {}, []   
    df['Workout Date'] = df['Workout Date'].apply(lambda x: parse_date(str(x)))
    
    for index, row in df.iterrows():
        date_string = str(row['Workout Date'])
        if isinstance(row['Workout Date'], pd._libs.tslibs.nattype.NaTType):
            invalid_dates.append((index, date_string))
        else:
            date_format = re.sub(r'\d+', '%', date_string)
            if date_format in date_formats:
                date_formats[date_format] += 1
            else:
                date_formats[date_format] = 1
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['Workout Date'])
    rows_dropped_invalid_date = len(invalid_dates)    
    # print(f"Dropped {rows_dropped_invalid_date} rows with invalid dates.")  ** ADD TO A REPORT **
    # print(f"Final number of rows: {len(df)}") ** ADD TO A REPORT **
    
    # Replace NaN values with None
    df = df.where(pd.notnull(df), None)

    # Replace infinite values with None
    df = df.replace([np.inf, -np.inf], None)

    # Reset the index after dropping rows
    df = df.reset_index(drop=True)

    return df