import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np

def load_csv():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        try:
            data = pd.read_csv(filepath)
            examine_data(data)
        except Exception as e:
            update_status(f"Error: {str(e)}")

def examine_data(data):
    try:
        attribute_count = data.shape[1]
        case_count = data.shape[0]
        balanced_status = "Unknown"
        
        if 'class' in data.columns:
            class_count = data['class'].nunique()
            cases_per_class = data['class'].value_counts()
            balanced_status = "Yes" if cases_per_class.nunique() == 1 else "No"
            cases_per_class = cases_per_class.to_dict()
            # Exclude 'class' column from numerical check
            non_class_columns = data.drop(columns=['class'])
        else:
            class_count = "No class column"
            cases_per_class = {}
            non_class_columns = data  # Check all columns if 'class' column is not present

        missing_data = data.isnull().sum().sum()
        all_numerical = "Yes" if non_class_columns.select_dtypes(exclude=[np.number]).empty else "No"

        # Update the labels with the results
        update_status(
            f"Attribute Count: {attribute_count}\n"
            f"Case Count: {case_count}\n"
            f"Class Count: {class_count}\n"
            f"Cases per Class: {cases_per_class}\n"
            f"Missing Fields: {missing_data}\n"
            f"All Fields Numerical: {all_numerical}\n"
            f"Balanced Status: {balanced_status}"
        )
    except Exception as e:
        update_status(f"Error: {str(e)}")

def update_status(message):
    status_label.config(text=message)

def main():
    global status_label
    root = tk.Tk()
    root.title("CSV Analyzer")
    
    # Set default window size
    root.geometry('400x200')

    tk.Button(root, text="Load CSV", command=load_csv).pack(pady=20)
    
    # Status label for displaying results
    status_label = tk.Label(root, text="", justify=tk.LEFT, anchor="w", font=('TkDefaultFont', 10), relief=tk.SUNKEN)
    status_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
