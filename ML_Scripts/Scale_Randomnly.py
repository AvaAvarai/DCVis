# Scale_Randomnly.py is a script that scales the values of each row in a CSV file by a random amount within a certain range.
# Used for data augmentation in machine learning projects.

import pandas as pd
import numpy as np


def adjust_csv_row_proportions(input_csv, output_csv):
    """Adjusts the values of each row in a CSV file by a random amount within a certain range.

    Args:
        input_csv (str): The file path to the input CSV file.
        output_csv (str): The file path to save the adjusted CSV file.

    Raises:
        ValueError: If the input CSV does not contain a 'class' column.
    """
    
    # Load the CSV into a pandas DataFrame
    df = pd.read_csv(input_csv)
    
    # Check for 'class' column
    if 'class' not in df.columns:
        raise ValueError("CSV must contain a 'class' column.")
    
    # Separate the 'class' column
    labels = df['class']
    df_numerical = df.drop(columns=['class'])
    
    # Calculate the minimum and maximum value for each column
    min_vals = df_numerical.min()
    max_vals = df_numerical.max()
    
    # Adjust each row within the range of the original data
    adjusted_rows = []
    for _, row in df_numerical.iterrows():
        adjustment = np.random.uniform(-1, 1, size=len(row)) * (max_vals - min_vals) * 0.1  # Max 10% adjustment
        adjusted_row = np.clip(row + adjustment, min_vals, max_vals)
        adjusted_rows.append(adjusted_row)
    
    # Create a new DataFrame from the adjusted rows
    df_adjusted = pd.DataFrame(adjusted_rows, columns=df_numerical.columns)
    df_adjusted['class'] = labels.values  # Reattach 'class' column
    
    # Save the adjusted DataFrame to a new CSV file
    df_adjusted.to_csv(output_csv, index=False)

def adjust_csv_row_proportions_no_bounds(input_csv, output_csv):
    """Adjusts the values of each row in a CSV file by a random amount without considering min/max values.

    Args:
        input_csv (str): The file path to the input CSV file.
        output_csv (str): The file path to save the adjusted CSV file.

    Raises:
        ValueError: If the input CSV does not contain a 'class' column.
    """
    
    # Load the CSV into a pandas DataFrame
    df = pd.read_csv(input_csv)
    
    # Check for 'class' column
    if 'class' not in df.columns:
        raise ValueError("CSV must contain a 'class' column.")
    
    # Temporarily remove the 'class' column
    labels = df['class']
    df_numerical = df.drop(columns=['class'])
    
    # Adjust each row with a random constant, not considering min/max values
    adjusted_rows = []
    for _, row in df_numerical.iterrows():
        adjustment = np.random.uniform(-1, 1, size=len(row))  # Uniform distribution
        adjusted_row = row + adjustment
        adjusted_rows.append(adjusted_row)
    
    # Create a new DataFrame from the adjusted rows
    df_adjusted = pd.DataFrame(adjusted_rows, columns=df_numerical.columns)
    df_adjusted['class'] = labels.values  # Reattach 'class' column
    
    # Save the adjusted DataFrame to a new CSV file
    df_adjusted.to_csv(output_csv, index=False)


adjust_csv_row_proportions_no_bounds('datasets\\fisher_iris.csv', 'datasets\\output_adjusted3.csv')

