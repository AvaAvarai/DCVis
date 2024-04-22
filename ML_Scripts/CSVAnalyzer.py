import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE

# Global variable to store the current DataFrame
current_data = None
smote_button = None  # Global reference to the SMOTE button


def adjust_csv_row_proportions():
    """Adjusts the values of each row in the current CSV data by a random amount within a certain range."""

    global current_data

    # Check for 'class' column
    if 'class' not in current_data.columns:
        messagebox.showerror("Error", "CSV must contain a 'class' column.")
        return

    # Separate the 'class' column
    labels = current_data['class']
    df_numerical = current_data.drop(columns=['class'])

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
    current_data = pd.DataFrame(adjusted_rows, columns=df_numerical.columns)
    current_data['class'] = labels.values  # Reattach 'class' column

    # Update display
    display_data(current_data)

def adjust_csv_row_proportions_no_bounds():
    """Adjusts the values of each row in the current CSV data by a random amount without considering min/max values."""

    global current_data

    # Check for 'class' column
    if 'class' not in current_data.columns:
        messagebox.showerror("Error", "CSV must contain a 'class' column.")
        return

    # Temporarily remove the 'class' column
    labels = current_data['class']
    df_numerical = current_data.drop(columns=['class'])

    # Adjust each row with a random constant, not considering min/max values
    adjusted_rows = []
    for _, row in df_numerical.iterrows():
        adjustment = np.random.uniform(-1, 1, size=len(row))  # Uniform distribution
        adjusted_row = row + adjustment
        adjusted_rows.append(adjusted_row)

    # Create a new DataFrame from the adjusted rows
    current_data = pd.DataFrame(adjusted_rows, columns=df_numerical.columns)
    current_data['class'] = labels.values  # Reattach 'class' column

    # Update display
    display_data(current_data)

def save_csv():
    if current_data is None:
        messagebox.showerror("Error", "No data to save. Please load or adjust data first.")
        return

    output_file = filedialog.asksaveasfilename(filetypes=[("CSV files", "*.csv")], defaultextension=".csv")
    if output_file:
        current_data.to_csv(output_file, index=False)
        messagebox.showinfo("Success", "CSV file has been saved.")

def update_smote_button():
    """Updates the enabled/disabled status of the SMOTE button based on the balance of the class column."""
    global current_data, smote_button
    if current_data is None or 'class' not in current_data.columns:
        smote_button['state'] = 'disabled'
        return
    
    # Check if data is balanced
    class_counts = current_data['class'].value_counts()
    if class_counts.nunique() == 1:  # All class counts are the same
        smote_button['state'] = 'disabled'
    else:
        smote_button['state'] = 'normal'

def load_csv():
    global current_data
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        try:
            current_data = pd.read_csv(filepath)
            display_data(current_data)
            update_smote_button()  # Update the SMOTE button status based on new data
        except Exception as e:
            update_status(f"Error: {str(e)}")

def apply_smote():
    global current_data

    if current_data is None:
        messagebox.showerror("Error", "No data loaded. Please load data first.")
        return
    
    # Separate features and target variable
    X = current_data.drop('class', axis=1)
    y = current_data['class']

    # Apply SMOTE
    smote = SMOTE(random_state=42)
    X_smote, y_smote = smote.fit_resample(X, y)

    # Concatenate the features and labels back into a DataFrame
    balanced_data = pd.concat([X_smote, y_smote.rename('class')], axis=1)

    # Update the global current_data with the balanced dataset
    current_data = balanced_data

    # Update display
    display_data(current_data)
    update_smote_button()  # Re-check if SMOTE should be enabled or disabled

    messagebox.showinfo("Success", "SMOTE applied successfully. Data is balanced now.")

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

def adjust_and_save_csv(adjustment_function):
    if current_data is None:
        messagebox.showerror("Error", "No CSV loaded. Please load a CSV file first.")
        return
    
    output_file = filedialog.asksaveasfilename(filetypes=[("CSV files", "*.csv")])
    if output_file:
        try:
            adjustment_function(current_data, output_file)
            messagebox.showinfo("Success", "CSV file has been adjusted and saved.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def main():
    global tree, status_label, smote_button
    root = tk.Tk()
    root.title("CSV Analyzer")

    # Define the window size
    window_width = 800
    window_height = 600

    # Get the screen dimension
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Find the center position
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)

    # Set the position of the window to the center of the screen
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    # Function to exit application on Esc key press
    def on_esc_press(event):
        root.quit()

    # Bind Esc key to the on_esc_press function
    root.bind('<Escape>', on_esc_press)

    # Button to load CSV
    load_button = tk.Button(root, text="Load CSV", command=load_csv)
    load_button.grid(row=0, column=0, padx=5, pady=5)

    # Button to apply SMOTE, initially disabled
    smote_button = tk.Button(root, text="Apply SMOTE", command=apply_smote, state='disabled')
    smote_button.grid(row=1, column=3, padx=5, pady=5)

    # Button to adjust row proportions with bounds
    adjust_button = tk.Button(root, text="Adjust Row Proportions", command=adjust_csv_row_proportions)
    adjust_button.grid(row=1, column=0, padx=5, pady=5)

    # Button to save the adjusted CSV
    save_button = tk.Button(root, text="Save CSV", command=save_csv)
    save_button.grid(row=0, column=3, padx=5, pady=5)

    # Button to adjust row proportions without bounds
    adjust_no_bounds_button = tk.Button(root, text="Adjust Row Proportions No Bounds", command=adjust_csv_row_proportions_no_bounds)
    adjust_no_bounds_button.grid(row=1, column=1, padx=5, pady=5, columnspan=2)  # Span across two columns for visual balance

    # Treeview widget for displaying CSV data
    tree = ttk.Treeview(root)
    tree.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

    # Status label for displaying results
    status_label = tk.Label(root, text="", justify=tk.LEFT, anchor="w", font=('TkDefaultFont', 10), relief=tk.SUNKEN)
    status_label.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky='ew')

    # Configure the grid to allow the Treeview to expand and to distribute space evenly
    root.grid_rowconfigure(2, weight=1)  # Make the Treeview row expandable
    for i in range(4):
        root.grid_columnconfigure(i, weight=1)  # Make all columns expand evenly

    root.mainloop()

if __name__ == "__main__":
    main()
