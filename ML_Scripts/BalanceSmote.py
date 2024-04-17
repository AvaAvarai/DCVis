import pandas as pd
from imblearn.over_sampling import SMOTE
import argparse

# Set up command line argument parsing
parser = argparse.ArgumentParser(description="Apply SMOTE to the entire dataset and export the balanced dataset.")
parser.add_argument("csv_name", type=str, help="Path to the CSV file containing the dataset.")
parser.add_argument("output_csv_name", type=str, help="Path to the output CSV file for the balanced dataset.")
args = parser.parse_args()

# Load data from CSV file
data = pd.read_csv(args.csv_name)

# Separate features and target variable
X = data.drop('class', axis=1)  # drop the class column from the features
y = data['class']  # extract only the class column for the target variable

# Apply SMOTE
smote = SMOTE(random_state=42)
X_smote, y_smote = smote.fit_resample(X, y)

# Concatenate the features and labels back into a DataFrame
balanced_data = pd.concat([X_smote, y_smote], axis=1)

# Save the balanced dataset to a new CSV file
balanced_data.to_csv(args.output_csv_name, index=False)

# Print the new class distribution and a success message
print(pd.Series(y_smote).value_counts())
print(f"Balanced dataset has been saved to {args.output_csv_name}.")
