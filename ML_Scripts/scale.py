import pandas as pd
import numpy as np

def adjust_csv_row_proportions(input_csv, output_csv):
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

# Example usage
adjust_csv_row_proportions('fisher_iris.csv', 'output_adjusted.csv')

