import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
import numpy as np
from sklearn.manifold import MDS, TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

data = None
reduced_data = None

def pick_file():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if filepath:
        file_label.config(text=filepath)
        global data
        data = pd.read_csv(filepath)
        display_statistics()

def display_statistics():
    if data is None:
        messagebox.showinfo("Error", "No data loaded!")
        return

    text = f"Sample Count: {len(data)}\n"
    text += f"Attribute Count: {len(data.columns)}\n"

    if 'class' in data.columns:
        classes = data['class'].value_counts()
        text += f"Class Count: {len(classes)}\n"
        text += "Samples per Class:\n" + "\n".join(f"{cls}: {count}" for cls, count in classes.items()) + "\n"

        # Range per attribute per class
        text += "Data Range per Attribute per Class:\n"
        grouped = data.groupby('class')
        for name, group in grouped:
            text += f"\nClass {name}:\n"
            for col in data.columns:
                if col != 'class':
                    text += f"{col}: {group[col].min()} to {group[col].max()}\n"
    else:
        text += "No class column available."

    original_stats_text.config(state='normal')
    original_stats_text.delete('1.0', tk.END)
    original_stats_text.insert(tk.END, text)
    original_stats_text.config(state='disabled')

def get_components(method):
    components = simpledialog.askinteger("Input", f"Enter the number of components for {method}:",
                                         parent=root, minvalue=1, maxvalue=min(data.shape)-1)
    if components is not None:
        apply_reduction(method, components)

def apply_reduction(method, n_components):
    if data is None:
        messagebox.showinfo("Error", "No data loaded!")
        return

    if 'class' not in data.columns:
        messagebox.showinfo("Error", "No class column found in data!")
        return

    if method == 'PCA':
        model = PCA(n_components=n_components)
    elif method == 'MDS':
        model = MDS(n_components=n_components)
    elif method == 'TSNE':
        model = TSNE(n_components=n_components)
    else:
        messagebox.showinfo("Info", f"{method} is not implemented yet")
        return

    # Normalize data (exclude the 'class' column from scaling)
    numeric_data = data.select_dtypes(include=[np.number])
    data_scaled = StandardScaler().fit_transform(numeric_data)

    # Apply reduction
    results = model.fit_transform(data_scaled)
    global reduced_data
    reduced_data = pd.DataFrame(results, columns=[f'Component {i+1}' for i in range(n_components)])

    # Append the class column to the reduced data
    reduced_data['class'] = data['class'].values

    show_statistics(reduced_stats_text, reduced_data)

def show_statistics(text_widget, dataframe):
    text_widget.config(state='normal')
    text_widget.delete('1.0', tk.END)
    text_widget.insert(tk.END, str(dataframe.describe()))
    text_widget.config(state='disabled')

def save_data():
    if reduced_data is None:
        messagebox.showinfo("Error", "No reduced data to save!")
        return

    filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if filepath:
        # Save without the index and ensure no comma precedes the first column
        reduced_data.to_csv(filepath, index=False)
        messagebox.showinfo("Success", "Data saved successfully!")

root = tk.Tk()
root.title("Dimensionality Reduction Tool")

# File picker
file_label = tk.Label(root, text="No file selected", width=80, anchor="w")
file_label.grid(row=0, column=1, padx=10, pady=10)
file_picker_button = tk.Button(root, text="Pick File", command=pick_file)
file_picker_button.grid(row=0, column=0, padx=10, pady=10)

# Reduction buttons with component input
buttons = {'PCA': lambda: get_components('PCA'), 'MDS': lambda: get_components('MDS'), 'TSNE': lambda: get_components('TSNE')}
for i, (method, action) in enumerate(buttons.items(), start=1):
    button = tk.Button(root, text=method, command=action)
    button.grid(row=i, column=0, columnspan=2, padx=10, pady=5)

# Save to file button
save_button = tk.Button(root, text="Save to File", command=save_data)
save_button.grid(row=len(buttons)+1, column=0, columnspan=2, padx=10, pady=10)

# Data statistics display
original_stats_text = tk.Text(root, height=10, width=40)
original_stats_text.grid(row=len(buttons)+2, column=0, padx=10, pady=10)
original_stats_text.config(state='disabled')

reduced_stats_text = tk.Text(root, height=10, width=40)
reduced_stats_text.grid(row=len(buttons)+2, column=1, padx=10, pady=10)
reduced_stats_text.config(state='disabled')

# Center window on screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (root.winfo_reqwidth() / 2))
y = int((screen_height / 2) - (root.winfo_reqheight() / 2))
root.geometry(f"+{x}+{y}")

root.mainloop()
