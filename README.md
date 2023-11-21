# DCVis: Dynamic Coordinate Visualisation System

## Project history

Continuation of a [CS Masters Project at CWU](https://github.com/Charles57-CWU/DSCVis).
Rebuild of former development during research assistance [lab project](https://github.com/CWU-VKD-LAB/DCVis).
Now built on a refactored base with a Model-View-Controller architecture and precise zoom & panning controls during self-study and directed research.

## About

This application displays multi-dimensional numerical data in 2D using OpenGL for GPU rendering. The plot can be panned around and zoomed in/out. Classes can be hidden, specified attribute markers can be customized, classes can be reordered and recolored. A box-clipping algorithm is included to clip lines and return contained samples of the dataset as a training and validation dataset split for machine learning analysis.

This visualization tool features multiple visualisation plots, including Parallel Coordinates, Paired Coordinates, Dynamic Scaffold Coordinates 1, Dynamic Scaffold Coordinates 2, Static Circular Coordinates. Additional multidimensional plots can be added with ease as the plot context class uses general vertices.

## Datasets

Requirements of datasets:

- .txt or .csv format
- include headers
- one label column and any number of feature columns
- label header must be 'class'
- Features must be numerical

Example dataset:

length,width,height,class  
2.7,3.5,3.2,dog  
1.2,5.5,2.1,cat  
2.5,4.1,1.6,dog  
1.0,1.0,1.0,cow

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

## Language and Libraries

Written in Python using 3.11 with the libraries:
pyopengl wheel pyopengl-accelerate pyqt6 numpy pandas scikit-learn

QTDesigner used for .UI file design used by PyQt6.

See `requirements.txt` for the development environment libraries listing.

## Features

- scroll-wheel click and drag on plot to pan the plot.
- Scroll the mouse wheel to zoom in/out of the plot.
- Right click twice to make a box clipping rectangle. The 1st right click is the upper right corner, and the 2nd right click is the bottom left corner.
- The cells in the class and attribute tables can be dragged and dropped to switch their orders.
- The slider below the attribute table will change the transparency of the attribute markers that are not selected in the highlight column.

Application window with 4D Fisher Iris dataset in first visualisation
![window](/screenshots/APP_WINDOW.png)

MNIST on DSC2 using t-SNE as scaffold origin points. Image contains 3,120,000 data points (60,000 * 52)
![mnist](/screenshots/MNIST.png)

Showing zoom and pan capabilities
![mnist](/screenshots/MNIST_ZOOM.png)

### Dev Plans

- Class Ordering Get Working
  - Bug 1: Reordering classes highlighs wrong polylines
  - Bug 2: Reordering classes makes marker checkbox not coresspond to correct class

- Circular Coordinates
  - Add Dynamic Circular Coordinates

- Attribute Optimization
  - n-epoch search
  - LDA based
  - SVM based
  - Hyperparam Tuning search

- Histogram View
  - Along axes each plot type

- Draggable n-D points
  - renormalize
  - replot

- Draggable Classification Boundary
  - n-epoch search
  - Update on drag
  - Show confusion matrix
  - LDA based
  - SVM based
  - Hyperparam tuning search
