# DCVis: Dynamic Coordinate Visualization System

DCVis is a Visual Knowledge Discovery (VKD) tool developed as part of an Artificial Intelligence and Machine Learning (AI/ML) research project at Central Washington University's Visual Knowledge Discovery Lab. The project spans from 2022 to 2024 and is still ongoing. Contributors are Alice Williams, James Battistoni IV, Charles Recaido, and Dr. Boris Kovalerchuk.

This software enables users to interactively construct visual ML models and explore multidimensional/multivariate data through General Line Coordinate visualizations. Features include interactive classification tools and synthetic data generation, shown to enhance supervised learning classifier models.

## Key Publications

- **Synthetic Data Generation and Automated Multidimensional Data Labeling for AI/ML in General and Circular Coordinates** by Alice Williams and Dr. Boris Kovalerchuk
- **Interpretable Machine Learning for Self-Service High-Risk Decision-Making** by Charles Recaido and Dr. Boris Kovalerchuk

DCVis is a complete rebuild of the [DSCVis](https://github.com/Charles57-CWU/DSCVis) software, incorporating new visualizations and enhanced tooling. The DCVis software is freely available under the MIT License, permitting both personal and commercial use.

## Requirements

- Python 3.x: Recommended Python 3.6 or higher for compatibility.
- Libraries installed from requirements.txt: Use pip to install the required libraries. Run the following command in the terminal: `pip install -r requirements.txt`

## Running

Execute `DCVIS_MAIN.py` script to launch the DCVis application: `python DCVIS_MAIN.py`

## Software Features

DCVis offers a robust suite of tools for visualizing and analyzing multidimensional numerical data. Here's what you can do with DCVis:

### Visualization

- **2D Visualizations**: Utilize OpenGL to render multidimensional numerical data from .csv or .txt files.
- **Interactive Plotting**: Engage with plots through panning, zooming, and selecting different color and transparency options.
- **Dynamic Visualization**: Reorder or invert axes to uncover patterns in n-D data, enhancing visual exploration.

### Data Interaction

- **Clipping Tools**: Use dual-right click clipping to highlight, analyze, export, or hide data for detailed analysis.
- **Point Selection**: Interactively select points or samples directly on the plot for detailed examination.

### Classification and Analysis

- **Rule-Based Classification**: Construct visual machine learning models by creating and combining classification rules.
- **Enhanced Learning Models**: Improve supervised learning classifiers using interactive tools and synthetic data generation.

### Customization

- **Configurable Display**: Customize background, class, and axes colors to suit different visualization needs.
- **Visibility Toggles**: Show or hide axes, points, connecting lines, and other elements to focus on relevant data.
- **Trace Mode**: Use alternating colors to trace data points across different visualization schemes.

### User Interface Enhancements

- **Interactive UI Elements**: Easily manage data and visualization settings with intuitive controls and UI elements.
- **Hotkeys and Shortcuts**: Access frequently used functions quickly with keyboard shortcuts.

These features are designed to facilitate an interactive, user-friendly experience for both novice and expert users, making complex data analysis more accessible and efficient.

## Controls

### Mouse Interactions

- **Pan Plot**: Click and drag with the scroll-wheel to pan the plot.
- **Zoom**: Scroll the mouse wheel to zoom in or out.
- **Box Clipping**: Right-click twice to create a clipping rectangle (first click sets the upper right corner, second click sets the bottom left corner).
- **Select Point**: Left-click to select a single point or multiple sample points.

### Keyboard Shortcuts

- **Cycle Selections**: Use the `Q` and `E` keys to cycle through the currently selected sample(s).
- **Adjust Vertical Position**: The `W` and `S` keys move the selected cases up or down proportionally.
- **Delete Samples**: Press the `D` key to delete the selected samples from the dataset.
- **Print Samples**: Press the `P` key to print the details of the selected samples.
- **Clone Samples**: Press the `C` key to create a synthetic copy of the selected samples.

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

## Dataset Requirements

DCVis is designed to work with structured numerical datasets to ensure compatibility and optimal functionality. Here are the specific requirements for datasets used in DCVis:

- **File Format**: The dataset must be in either `.txt` or `.csv` file format.
- **Header Row**: Each dataset file must include a header row. The headers specify the names of the features and the label column.
- **Label Column**: There must be one column specifically designated for labels, identified by the header name 'class'.
- **Feature Columns**:
  - The number of feature columns can vary.
  - Each feature column must be labeled in the header.
  - All data within feature columns must be numerical, as the software does not process textual or categorical data without pre-conversion to numerical formats.

These requirements ensure that the data is properly recognized and processed by DCVis, facilitating accurate and meaningful visualizations.

## Visualizations Supported

Generalized vertex class included for adding visualization methods.  
This visualization tool features multiple visualisation methods:

- Parallel Coordinates (PC) ![PC](/screenshots/PC.png)
- Shifted Paired Coordinates (SPC) ![SPC](/screenshots/SPC.png)
- Dynamic Scaffold Coordinates 1 (DSC1) ![DSC1](/screenshots/DSC1.png)
- Dynamic Scaffold Coordinates 2 (DSC2) ![DSC2](/screenshots/DSC2.png)
- Static Circular Coordinates (SCC) ![SCC](/screenshots/SCC.png)
- Dynamic Circular Coordinates (DCC) ![DCC](/screenshots/DCC.png)
