import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

# Define the GLC-L function
def calculate_angle(coefficient):
    return np.arccos(coefficient)

def glc_linear(data, coefficients):
    transformed_data = []
    num_rows = data.shape[0]
    num_columns = data.shape[1]
    for i in range(num_rows):
        x, y = 0, 0
        coordinates = [(x, y)]
        for j in range(num_columns):
            radius = data[i, j]
            angle = calculate_angle(coefficients[j])
            new_x = x + radius * np.cos(angle)
            new_y = y + radius * np.sin(angle)
            coordinates.append((new_x, new_y))
            x, y = new_x, new_y
        transformed_data.append(coordinates)
    return transformed_data

def plot_glc_data(class_data, color, label):
    for instance in class_data:
        xs, ys = zip(*instance)
        plt.plot(xs, ys, color=color, label=label)
        plt.scatter(xs[-1], ys[-1], color='black', edgecolor='white', zorder=5)  # Endpoint marker
        label = "_nolegend_"  # Only show legend once

def plot_xC_lines(class_data, color, label):
    xs_end = [instance[-1][0] for instance in class_data]
    min_x = min(xs_end)
    max_x = max(xs_end)
    plt.axvline(x=min_x, color=color, linestyle='--', linewidth=1, label=f'{label} min x line')
    plt.axvline(x=max_x, color=color, linestyle='--', linewidth=1, label=f'{label} max x line')

def visualize_data(data, target, class1, class2, class1_name, class2_name):
    filtered_data = data[(target == class1) | (target == class2)]
    filtered_target = target[(target == class1) | (target == class2)]
    lda = LinearDiscriminantAnalysis(n_components=1)
    lda_transformed = lda.fit_transform(filtered_data, filtered_target)
    lda_coefficients = lda.coef_[0]
    lda_coefficients_normalized = lda_coefficients / np.max(np.abs(lda_coefficients))
    transformed_data_lda = glc_linear(filtered_data, lda_coefficients_normalized)
    class_1_lda = [transformed_data_lda[i] for i in range(len(filtered_target)) if filtered_target[i] == class1]
    class_2_lda = [transformed_data_lda[i] for i in range(len(filtered_target)) if filtered_target[i] == class2]
    class_2_lda_flipped = [[(x, -y) for x, y in instance] for instance in class_2_lda]

    plt.figure(figsize=(10, 8))
    plot_glc_data(class_1_lda, 'b', class1_name)
    plot_glc_data(class_2_lda_flipped, 'g', f'{class2_name} (Flipped)')
    plot_xC_lines(class_1_lda, 'b', class1_name)
    plot_xC_lines(class_2_lda_flipped, 'g', f'{class2_name} (Flipped)')
    plt.axhline(y=0, color='black', linestyle='-', linewidth=1, label='y = 0 line')
    plt.legend()
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title(f'GLC-L ({class1_name} v. {class2_name}) using LDA Angles with Projection Lines')
    plt.show()

def load_data():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        data = pd.read_csv(file_path)
        if 'class' not in data.columns:
            messagebox.showerror("Error", "Dataset must have a 'class' column.")
            return

        unique_classes = data['class'].unique()
        if len(unique_classes) != 2:
            messagebox.showerror("Error", "Dataset must have exactly two classes.")
            return

        global loaded_data, class1_name, class2_name, feature_data, target_data
        loaded_data = data
        class1_name = unique_classes[0]
        class2_name = unique_classes[1]
        feature_data = data.drop(columns=['class']).values
        target_data = data['class'].values

        class1_count = sum(target_data == class1_name)
        class2_count = sum(target_data == class2_name)

        stats = f"File: {file_path}\n"
        stats += f"Total cases: {len(data)}\n"
        stats += f"Class 1: {class1_name} ({class1_count} cases)\n"
        stats += f"Class 2: {class2_name} ({class2_count} cases)\n"

        stats_text.delete(1.0, tk.END)
        stats_text.insert(tk.END, stats)

def visualize():
    if loaded_data is not None:
        visualize_data(feature_data, target_data, class1_name, class2_name, str(class1_name), str(class2_name))
    else:
        messagebox.showerror("Error", "No dataset loaded.")

root = tk.Tk()
root.title("GLC-L Visualization")

loaded_data = None

load_button = tk.Button(root, text="Load Dataset", command=load_data)
load_button.pack(pady=10)

visualize_button = tk.Button(root, text="Visualize", command=visualize)
visualize_button.pack(pady=10)

stats_text = tk.Text(root, height=10, width=50)
stats_text.pack(pady=10)

exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=10)

root.mainloop()
