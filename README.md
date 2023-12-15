# DCVis: Dynamic Coordinate Visualisation System

## About

This application displays multi-dimensional numerical data in 2D visualizations using OpenGL for GPU rendering. The plot can be interacted with, panning around, zooming in/out, configuring view, and exploring data interactively. Data may be highlighted with dual-right click clipping, analyzed, and exported or hidden for further analysis. For building visual machine learning models using visualization region rules-based classification. Combining and chaining rules to produce classifiers for unseen data.

## Visualization Methods

Generalized vertex class included for adding visualization methods.  
This visualization tool features multiple visualisation methods:

- Parallel Coordinates (PC) ![PC](/screenshots/PC.png)
- Shifted Paired Coordinates (SPC) ![SPC](/screenshots/SPC.png)
- Dynamic Scaffold Coordinates 1 (DSC1) ![DSC1](/screenshots/DSC1.png)
- Dynamic Scaffold Coordinates 2 (DSC2) ![DSC2](/screenshots/DSC2.png)
- Static Circular Coordinates (SCC) ![SCC](/screenshots/SCC.png)
- Dynamic Circular Coordinates (DCC) ![DCC](/screenshots/DCC.png)

## Datasets

Dataset requirements:

- Format of .txt or .csv
- Header row required
- One label column denoted 'class' in header
- Any number of feature columns attribute name in header
- Features must be numerical data

Datasets included:

- Fisher Iris of flower measurements -- 150 samples, 4 features, 3 classes
- Breast Cancer Wisconsin diagnostics -- 569 samples, 30 features, 2 classes
- Diabetes diagnostics -- 768 samples, 8 features, 2 classes
- Heart Disease diagnostics -- 1,025 samples, 13 features, 2 classes
- Ionosphere atmosphere readings -- 351 samples, 34 features, 2 classes (some empty cells)
- MNIST Capital Letters handwriting -- 20,000 samples, 16 features, 26 classes
- Sinusoidal wave samplings -- 200 samples, 2 features, 2 classes
- Wheat Seed variety measurements -- 210 samples, 7 features, 3 classes
- Wine chemical analysis measurements -- 4,898 samples, 11 features, 7 classes
- Artificial testing datasets

## Program Features

- scroll-wheel click and drag on plot to pan the plot.
- Scroll the mouse wheel to zoom in/out of the plot.
- Right click twice to make a box clipping rectangle. The 1st right click is the upper right corner, and the 2nd right click is the bottom left corner.
- Clipped samples are highlighted, 'Hide Clips' button will suppress clipped samples from being drawn, 'Remove Clips' button will restore.
- The cells in the class and attribute tables can be dragged and dropped to switch their orders.
- The slider below the attribute table will change the transparency of the attribute markers that are not selected in the highlight column.

Iris on PC with 4D Fisher Iris dataset of 150 data points with Setosa class highlighted.
![Classify Setosa](/screenshots/IRIS_SETOSA_CLASSIFY.png)

## Language and Libraries

Written in Python using 3.11 with the libraries:
pyopengl wheel pyopengl-accelerate pyqt6 numpy pandas scikit-learn

QTDesigner used for .UI file design used by PyQt6.

See `requirements.txt` for the development environment libraries listing.

## Project History

- Continuation of a [CS Masters Project at CWU](https://github.com/Charles57-CWU/DSCVis).
- Rebuild of former research [lab project](https://github.com/CWU-VKD-LAB/DCVis).
- Now built on a refactored MVC architecture with precise zoom & panning controls.
