# DCVis: Dynamic Coordinate Visualisation System

DCVis is a research project to build visual machine learning models with multidimensional visualizations and interactive classification tools.  
Techniques being ported to C for improved performance with [CVis](https://github.com/CWU-VKD-LAB/CVis).  

Contributors: Alice Williams, James Battistoni, Charles Recaido  
at Central Washington University Visual Knowledge Discovery Lab  
on projects by Dr. Boris Kovalerchuk during years 2022 to 2024.  

*This software is a rewrite of [DSCVis](https://github.com/Charles57-CWU/DSCVis) with new visualizations and tooling features.*  

## Requirements

- Python 3.x: Recommended Python 3.6 or higher for compatibility.
- Libraries installed from requirements.txt: Use pip to install the required libraries. Run the following command in the terminal: `pip install -r requirements.txt`

## Running

Execute `DCVIS_MAIN.py` script to launch the DCVis application: `python DCVIS_MAIN.py`

## Software Features

- Visualize multi-dimensional numerical data (.csv or .txt file) in 2D visualizations using OpenGL for GPU rendering.  
- Plot can be interacted with, panning around, zooming in/out, configuring view options, and exploring data interactively.  
- Data may be highlighted with dual-right click clipping, analyzed, and exported or hidden for further analysis.  
- Classification rules can be built from clipped samples.
- Axes can be inverted to further find n-D data patterns.
- For building visual machine learning models using rules-based classification. Combining and chaining rules to produce classifiers for future data.
- Background, class, and axes colors are each configurable.
- Axes can be shown or hidden.
- Trace mode alternates colors for visual tracing.

## Controls

- scroll-wheel click and drag on plot to pan the plot.
- Scroll the mouse wheel to zoom in/out of the plot.
- Right click twice to make a box clipping rectangle. The 1st right click is the upper right corner, and the 2nd right click is the bottom left corner.
- Left click to pick up single point of sample(s).
- Q and E keys to cycle currently selected sample(s).
- Clipped samples are highlighted, 'Hide Clips' button will suppress clipped samples from being drawn, 'Remove Clips' button will restore.
- The cells in the class and attribute tables can be dragged and dropped to switch their orders.
- The slider below the attribute table will change the transparency of the attribute markers that are not selected in the highlight column.
- Hotkeys listed next to user interface elements.

## Datasets included

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
