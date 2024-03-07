# DCVis: Dynamic Coordinate Visualisation System

## About DCVis

DCVis is an interactive visualization application for building machine learning models by visual exploration. Techniques being ported to C for improved performance with [CVis](https://github.com/CWU-VKD-LAB/CVis).  

This work is established by Dr. Boris Kovalerchuk and the Visual Knowledge Discovery and Imaging Lab of Central Washington University. We are greatly inspired by Dr. Alfred Inselberg who invented Parallel Coordinates.  

This software applies Visual Knowledge Discovery techniques which use dynamic tools to build machine learning models which are inherently explainable and interpretable using visual analytics.  

*This software is a rewrite of [DSCVis](https://github.com/Charles57-CWU/DSCVis) to support newly developed tooling features.*  

## DCVis Features

- Visualize multi-dimensional numerical data (.csv or .txt file) in 2D visualizations using OpenGL for GPU rendering.  
- Plot can be interacted with, panning around, zooming in/out, configuring view options, and exploring data interactively.  
- Data may be highlighted with dual-right click clipping, analyzed, and exported or hidden for further analysis.  
- Classification rules can be built from clipped samples.
- Axes can be inverted to find improved n-D data patterns.
- For building visual machine learning models using rules-based classification. Combining and chaining rules to produce classifiers for future data.

## Visualization Methods

Generalized vertex class included for adding visualization methods.  
This visualization tool features multiple visualisation methods:

- Parallel Coordinates (PC) ![PC](/screenshots/PC.png)
- Shifted Paired Coordinates (SPC) ![SPC](/screenshots/SPC.png)
- Dynamic Scaffold Coordinates 1 (DSC1) ![DSC1](/screenshots/DSC1.png)
- Dynamic Scaffold Coordinates 2 (DSC2) ![DSC2](/screenshots/DSC2.png)
- Static Circular Coordinates (SCC) ![SCC](/screenshots/SCC.png)
- Dynamic Circular Coordinates (DCC) ![DCC](/screenshots/DCC.png)

Attributes may be inverted to further engineer visualized features.
Iris in SPC with X1, X2 inverted:
![SPC inverted](/screenshots/SPC_INVERT_X1_X2.png)

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
- Artificial testing datasets which exhibit various properties of visualizations.

## Program Features

- scroll-wheel click and drag on plot to pan the plot.
- Scroll the mouse wheel to zoom in/out of the plot.
- Right click twice to make a box clipping rectangle. The 1st right click is the upper right corner, and the 2nd right click is the bottom left corner.
- Left click to pick up single point of sample(s).
- Q and E keys to cycle currently selected sample(s).
- Clipped samples are highlighted, 'Hide Clips' button will suppress clipped samples from being drawn, 'Remove Clips' button will restore.
- The cells in the class and attribute tables can be dragged and dropped to switch their orders.
- The slider below the attribute table will change the transparency of the attribute markers that are not selected in the highlight column.

Iris in PC with Setosa class highlighted and alpha brushing effect:
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

Authors working on this project: Alice Williams, James Battistoni, and Charles Recaido.

