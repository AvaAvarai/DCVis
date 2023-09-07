# DCVis: Dynamic Coordinate Visualisation System

Formerly for CS Masters Program at CWU, renewed for further research.

## About

This application displays multi-dimensional data in 2D using OpenGL for rendering. The plot can be dragged and zoomed in/out. Classes can be hidden, as well as specified attribute markers. A box-clipping algorithm is included to clip lines and return samples of the dataset.

This visualization tool features multiple visualisation plots, including Parallel Coordinates, Paired Coordinates, DSC1, and DSC2. Additional multidimensional plots can be added with ease as the plot context class uses general vertices.

## Dataset Information

- Dataset must be in .txt or .csv format
- Dataset must include headers
- Dataset should only include class and attribute columns
- Dataset class header must be labeled as "class" without quotations
- Dataset features besides "class" must be in numeric representation

### Example dataset

length,width,height,class  
2.7,3.5,3.2,dog  
1.2,5.5,2.1,cat  
2.5,4.1,1.6,dog  

### Language Used

Python 3.9  
PyOpenGL 3.1.5  
PyQt6  
numpy 1.21.4  
pandas 1.3.4  
scikit-learn 1.0.1  

QTDesigner not Required but the .UI file for PyQt6 was designed with.

### Functions

- scroll-wheel click and drag on plot to pan the plot.
- Scroll the mouse wheel to zoom in/out of the plot.
- Right click twice to make a box clipping rectangle. The 1st right click is the upper right corner, and the 2nd right click is the bottom left corner.
- The cells in the class and attribute tables can be dragged and dropped to switch their orders.
- The slider below the attribute table will change the transparency of the attribute markers that are not selected in the highlight column.

Application window with 4D Fisher Iris dataset in first visualisation
![window](/Images/APP_WINDOW.png)

MNIST on DSC2 using t-SNE as scaffold origin points. Image contains 3,120,000 data points (60,000 * 52)
![mnist](/Images/MNIST.png)

Showing zoom and pan capabilities
![mnist](/Images/MNIST_ZOOM.png)
