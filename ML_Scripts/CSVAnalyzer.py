import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import numpy as np

def load_csv():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        try:
            data = pd.read_csv(filepath)
            display_data(data)
            examine_data(data)
        except Exception as e:
            update_status(f"Error: {str(e)}")

def display_data(data):
    # Clear existing data in the Treeview
    for row in tree.get_children():
        tree.delete(row)
    
    # Set up the Treeview columns
    tree["columns"] = list(data.columns)
    tree["show"] = "headings"
    
    # Configure column headers
    for col in data.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="w")
    
    # Populate the Treeview with data rows
    for index, row in data.iterrows():
        tree.insert("", "end", values=list(row))

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
        else:
            class_count = "No class column"
            cases_per_class = {}
        
        missing_data = data.isnull().sum().sum()
        all_numerical = "Yes" if data.select_dtypes(exclude=[np.number]).empty else "No"
        
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
    global tree, status_label
    root = tk.Tk()
    root.title("CSV Analyzer")
    
    root.geometry('800x400')  # Larger size to accommodate the data display

    # Button to load CSV
    load_button = tk.Button(root, text="Load CSV", command=load_csv)
    load_button.pack(pady=10)

    # Treeview widget for displaying CSV data
    tree = ttk.Treeview(root)
    tree.pack(pady=10, padx=10, fill='both', expand=True)

    # Status label for displaying results
    status_label = tk.Label(root, text="", justify=tk.LEFT, anchor="w", font=('TkDefaultFont', 10), relief=tk.SUNKEN)
    status_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
