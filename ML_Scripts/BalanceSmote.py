import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import argparse

# Set up command line argument parsing
parser = argparse.ArgumentParser(description="Balance an imbalanced dataset using SMOTE and train a RandomForest model.")
parser.add_argument("csv_name", type=str, help="Path to the CSV file containing the dataset.")
parser.add_argument("output_csv_name", type=str, help="Path to the output CSV file for the balanced dataset.")
args = parser.parse_args()

# Load data from CSV file
data = pd.read_csv(args.csv_name)

# Separate features and target variable
X = data.drop('class', axis=1)  # drop the class column from the features
y = data['class']  # extract only the class column for the target variable

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Apply SMOTE
smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

# Concatenate the features and labels back into a DataFrame
balanced_data = pd.concat([X_train_smote, y_train_smote], axis=1)

# Save the balanced dataset to a new CSV file
balanced_data.to_csv(args.output_csv_name, index=False)
