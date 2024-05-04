# DCVis: Dynamic Coordinate Visualisation System

DCVis is a Visual Knowledge Discovery (VKD) Artificial Intelligence and Machine Learning (AI/ML) research project.  
This project allows for interactive building of visual ML models using multidimensional (n-D) data in visualizations.  
With interactive classification tools and synthetic data generation features supporting novel classifier improvement techniques.  

Project contributors: Alice Williams, James Battistoni IV, Charles Recaido, and Dr. Boris Kovalerchuk
at Central Washington University Visual Knowledge Discovery Lab, project during years 2022 to 2024.

Software developed for the paper:

- Synthetic Data Generation and Automated Multidimensional Data Labeling for AI/ML in General and Circular Coordinates by Alice Williams and Dr. Boris Kovalerchuk

Available under the MIT License, allowing for both personal and commercial use.

*This software is a rewrite of [DSCVis](https://github.com/Charles57-CWU/DSCVis) with new visualizations and tooling features.*  

## Requirements

- Python 3.x: Recommended Python 3.6 or higher for compatibility.
- Libraries installed from requirements.txt: Use pip to install the required libraries. Run the following command in the terminal: `pip install -r requirements.txt`

## Running

Execute `DCVIS_MAIN.py` script to launch the DCVis application: `python DCVIS_MAIN.py`

## Software Features

- Visualize multi-dimensional numerical data (.csv or .txt file) in 2D visualizations using OpenGL.  
- Plot can be interacted with through panning, zooming, color and transparency selection, and interactive point selection.  
- Data may be highlighted with dual-right click clipping, analyzed, and exported or hidden for further analysis.  
- Classification rules can be built from clipped cases.
- Axes can be reordered or inverted to further find n-D data patterns.
- For building visual machine learning models using rules-based classification. Combining and chaining rules to produce classifiers for future data.
- Background, class, and axes colors are each configurable.
- Axes, points, and connecting lines can be shown or hidden.
- Trace mode alternates colors for visual tracing.

## Controls

### Mouse Interactions

- **Pan Plot**: Click and drag with the scroll-wheel to pan the plot.
- **Zoom**: Scroll the mouse wheel to zoom in or out.
- **Box Clipping**: Right-click twice to create a clipping rectangle (first click sets the upper right corner, second click sets the bottom left corner).
- **Select Point**: Left-click to select a single point or multiple sample points.

### Keyboard Shortcuts

- **Cycle Selections**: Use the `Q` and `E` keys to cycle through the currently selected sample(s).
- **Adjust Vertical Position**: The `W` and `S` keys move the selected cases up or down proportionally.

### UI Elements

- **Highlight Clipped Cases**: Clipped cases are highlighted on the plot. Use the 'Add Classification Rule' button to convert current clipped rectangles into a new rule.
- **Rule Visibility**: Toggle the visibility of cases contained within a rule using the checkbox next to the rule.
- **Reorder Tables**: Drag and drop cells within the class and attribute tables to reorder them.
- **Adjust Transparency**: A slider below the attribute table adjusts the transparency of attribute markers not selected in the highlight column.

### Additional Information

- Hotkeys are provided next to relevant user interface elements for quick reference.

## Datasets included

- Fisher Iris of flower measurements -- 150 cases, 4 features, 3 classes
- Breast Cancer Wisconsin diagnostics -- 569 cases, 30 features, 2 classes
- WBC -- 696 cases, 9 features, 2 classes
- Diabetes diagnostics -- 768 cases, 8 features, 2 classes
- Heart Disease diagnostics -- 1,025 cases, 13 features, 2 classes
- Ionosphere atmosphere readings -- 351 cases, 34 features, 2 classes (some empty cells)
- MNIST Capital Letters handwriting -- 20,000 cases, 16 features, 26 classes
- Sinusoidal wave samplings -- 200 cases, 2 features, 2 classes
- Wheat Seed variety measurements -- 210 cases, 7 features, 3 classes
- Wine chemical analysis measurements -- 4,898 cases, 11 features, 7 classes

## Dataset requirements

- Format of .txt or .csv
- Header row required
- One label column denoted 'class' in header
- Any number of feature columns attribute name in header
- Features must be numerical data

## Visualizations Supported

Generalized vertex class included for adding visualization methods.  
This visualization tool features multiple visualisation methods:

- Parallel Coordinates (PC) ![PC](/screenshots/PC.png)
- Shifted Paired Coordinates (SPC) ![SPC](/screenshots/SPC.png)
- Dynamic Scaffold Coordinates 1 (DSC1) ![DSC1](/screenshots/DSC1.png)
- Dynamic Scaffold Coordinates 2 (DSC2) ![DSC2](/screenshots/DSC2.png)
- Static Circular Coordinates (SCC) ![SCC](/screenshots/SCC.png)
- Dynamic Circular Coordinates (DCC) ![DCC](/screenshots/DCC.png)
