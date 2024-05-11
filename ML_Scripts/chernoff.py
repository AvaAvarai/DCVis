import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arc
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.colors as mcolors

def draw_colored_face(features, species, ax, species_color_map):
    # Ensure we have a features array and its length
    num_features = len(features)
    
    # Basic face features
    face_color = species_color_map[species]
    face_size = features[0] * 2.5 + 0.5 if num_features > 0 else 0.5
    face = Circle((0.5, 0.5), face_size, color=face_color, zorder=1)
    ax.add_artist(face)

    # Eyes
    eye_size = features[2] * 0.15 + 0.05 if num_features > 2 else 0.05
    eye_x_spacing = features[3] * 0.7 + 0.5 if num_features > 3 else 0.5
    left_eye = Circle((0.5 - eye_x_spacing / 2, 0.6), eye_size, color='black', zorder=2)
    right_eye = Circle((0.5 + eye_x_spacing / 2, 0.6), eye_size, color='black', zorder=2)
    ax.add_artist(left_eye)
    ax.add_artist(right_eye)

    # Mouth
    mouth_length = features[1] * 0.6 + 0.2 if num_features > 1 else 0.2
    mouth = Arc((0.5, 0.35), mouth_length, 0.1, theta1=20, theta2=160, color='black', zorder=3)
    ax.add_artist(mouth)

    # Additional features based on the number of features available
    if num_features > 4:
        eyebrow_slant = features[4] * 30  # Slant angle
        left_eyebrow = Arc((0.5 - eye_x_spacing / 2, 0.65), 0.1, 0.05, theta1=0, theta2=180 + eyebrow_slant, color='black', zorder=3)
        right_eyebrow = Arc((0.5 + eye_x_spacing / 2, 0.65), 0.1, 0.05, theta1=180 - eyebrow_slant, theta2=360, color='black', zorder=3)
        ax.add_artist(left_eyebrow)
        ax.add_artist(right_eyebrow)

    if num_features > 5:
        nose_height = features[5] * 0.1 + 0.05
        nose = Arc((0.5, 0.5), 0.1, nose_height, theta1=250, theta2=290, color='black', zorder=3)
        ax.add_artist(nose)

    if num_features > 6:
        ear_size = features[6] * 0.1 + 0.05
        left_ear = Circle((0.3, 0.5), ear_size, color='black', zorder=1)
        right_ear = Circle((0.7, 0.5), ear_size, color='black', zorder=1)
        ax.add_artist(left_ear)
        ax.add_artist(right_ear)

    # Hide axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

def plot_data(filename):
    # Load data
    df = pd.read_csv(filename)
    features = df.iloc[:, :-1]
    classes = df.iloc[:, -1]

    # Normalize the features
    scaler = MinMaxScaler()
    features = scaler.fit_transform(features)

    # Generate color map for species
    unique_classes = classes.unique()
    colors = list(mcolors.TABLEAU_COLORS.values())  # More distinct colors
    species_color_map = {cls: colors[i % len(colors)] for i, cls in enumerate(unique_classes)}

    # Prepare the figure with appropriate subplot size
    fig, axes = plt.subplots(nrows=5, ncols=int(np.ceil(len(classes)/5)), figsize=(15, 8))

    # Draw Chernoff faces
    for ax, feature, cls in zip(axes.flatten(), features, classes):
        draw_colored_face(feature, cls, ax, species_color_map)

    # Create a legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=cls)
                       for cls, color in species_color_map.items()]
    fig.legend(handles=legend_elements, loc='lower center', ncol=len(unique_classes), fontsize='small')

    # Draw the canvas
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=1, column=0, columnspan=3)
    canvas.draw()

def open_file():
    filename = filedialog.askopenfilename(title="Select file", filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))
    if filename:
        plot_data(filename)

# Create main window
window = tk.Tk()
window.title("Dataset Visualization with Chernoff Faces")

# Add buttons and canvas
btn_load = tk.Button(window, text="Load Data", command=open_file)
btn_load.grid(row=0, column=0, sticky="nsew")

# Configure the grid
window.grid_rowconfigure(1, weight=1)  # Makes the row containing the canvas expandable
window.grid_columnconfigure(0, weight=1)  # Makes the column expandable

window.mainloop()
