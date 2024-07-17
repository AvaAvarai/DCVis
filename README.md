# DCVis: Dynamic Coordinate Visualization System

DCVis is a Visual Knowledge Discovery (VKD) tool developed at Central Washington University's Visual Knowledge Discovery Lab. Initiated in 2022, the project is built by Alice Williams, James Battistoni IV, Charles Recaido, and Dr. Boris Kovalerchuk.

DCVis allows users to interactively build visual ML models for classifying new data. It offers tools to explore multidimensional data using General Line Coordinate visualizations and includes features for interactive classification and synthetic data generation to enhance supervised learning models.

## Requirements

- Python 3.x: Recommended version 3.6 or higher (primarily developed on Python 3.10.6).
- Dependencies: Install libraries from requirements.txt by running `pip install -r requirements.txt` in the terminal.

## Setup

Project development is majorly done in Python virtual environments. The suggested setup instructions are:

1. **Download the project and open it in a terminal:**
   - Suggested download with git and open in an IDE with an integrated terminal.
2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   ```
   (The virtual environment will be named `venv`)
3. **Activate the virtual environment:**
   - The activation command depends on your operating system and shell. See the table below.
4. **Install the required libraries:**
   ```sh
   python -m pip install -r requirements.txt
   ```
5. **Start the application:**
   ```sh
   python DCVIS_MAIN.py
   ```

| Platform | Shell     | Command to activate virtual environment             |
|----------|-----------|-----------------------------------------------------|
| POSIX    | bash/zsh  | `$ source <venv>/bin/activate`                      |
|          | fish      | `$ source <venv>/bin/activate.fish`                 |
|          | csh/tcsh  | `$ source <venv>/bin/activate.csh`                  |
| PowerShell |         | `$ <venv>/bin/Activate.ps1`                         |
| Windows  | cmd.exe   | `C:\> <venv>\Scriptsctivate.bat`                  |
|          | PowerShell| `PS C:\> <venv>\Scripts\Activate.ps1`               |

Source: [Python Virtual Environments Documentation](https://docs.python.org/3/library/venv.html)

## Running

Execute `DCVIS_MAIN.py` script to launch the DCVis application: `python DCVIS_MAIN.py`

## Software Features

DCVis offers a tool suite for visualizing and analyzing multidimensional numerical (tabular) data. Here's what you can do with DCVis:

## Visualization Capabilities

- **2D Visualizations**: Utilize OpenGL to render multidimensional numerical data from .csv or .txt files.
- **Interactive Plotting**: Engage with plots through panning, zooming, and selecting different color and transparency options.
- **Dynamic Visualization**: Reorder or invert axes to uncover patterns in n-D data, enhancing visual exploration.

## Data Interaction

- **Clipping Tools**: Use dual-right click clipping to highlight, analyze, export, or hide data for detailed analysis.
- **Point Selection**: Interactively select points or samples directly on the plot for detailed examination.

## Classification and Analysis

- **Rule-Based Classification**: Construct visual machine learning models by creating and combining classification rules.
- **Enhanced Learning Models**: Improve supervised learning classifiers using interactive tools and synthetic data generation.

## Customization

- **Configurable Display**: Customize background, class, and axes colors to suit different visualization needs.
- **Visibility Toggles**: Show or hide axes, points, connecting lines, and other elements to focus on relevant data.
- **Trace Mode**: Use alternating colors to trace data points across different visualization schemes.

## User Interface Enhancements

- **Interactive UI Elements**: Easily manage data and visualization settings with intuitive controls and UI elements.
- **Hotkeys and Shortcuts**: Access frequently used functions quickly with keyboard shortcuts.

These features are designed to facilitate an interactive, user-friendly experience for both novice and expert users, making complex data analysis more accessible and efficient.

## Mouse Interactions

- **Pan Plot**: Click and drag with the scroll-wheel to pan the plot.
- **Zoom**: Scroll the mouse wheel to zoom in or out.
- **Box Clipping**: Right-click twice to create a clipping rectangle (first click sets the upper right corner, second click sets the bottom left corner).
- **Select Point**: Left-click to select a single point or multiple sample points.

## Keyboard Shortcuts

- **Cycle Selections**: Use the `Q` and `E` keys to cycle through the currently selected sample(s).
- **Adjust Vertical Position**: The `W` and `S` keys move the selected cases up or down proportionally.
- **Delete Samples**: Press the `D` key to delete the selected samples from the dataset.
- **Print Samples**: Press the `P` key to print the details of the selected samples.
- **Clone Samples**: Press the `C` key to create a synthetic copy of the selected samples.

## UI Elements

- **Highlight Clipped Cases**: Clipped cases are highlighted on the plot. Use the 'Add Classification Rule' button to convert current clipped rectangles into a new rule.
- **Rule Visibility**: Toggle the visibility of cases contained within a rule using the checkbox next to the rule.
- **Reorder Tables**: Drag and drop cells within the class and attribute tables to reorder them.
- **Adjust Transparency**: A slider below the attribute table adjusts the transparency of attribute markers not selected in the highlight column.

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

DCVis works with structured numerical datasets and requires a data format of:

  - File Format: .txt or .csv
  - Header Row: Must include headers for feature names and the label column.
  - Label Column: Must be named 'class'.
  - Feature Columns:
      - Variable number of columns
      - Labeled in the header
      - Must contain numerical data only

These requirements ensure proper data recognition and processing for accurate visualizations in DCVis. Datasets included meet these requirements.

## Visualizations Supported

Generalized vertex class included for adding visualization methods.  
This visualization tool features multiple visualisation methods:

- Parallel Coordinates (PC) ![PC](/screenshots/PC.png)
- Shifted Paired Coordinates (SPC) ![SPC](/screenshots/SPC.png)
- Dynamic Scaffold Coordinates 1 (DSC1) ![DSC1](/screenshots/DSC1.png)
- Dynamic Scaffold Coordinates 2 (DSC2) ![DSC2](/screenshots/DSC2.png)
- Static Circular Coordinates (SCC) ![SCC](/screenshots/SCC.png)
- Dynamic Circular Coordinates (DCC) ![DCC](/screenshots/DCC.png)

## Key Publications

- **[Preprint] Synthetic Data Generation and Automated Multidimensional Data Labeling for AI/ML in General and Circular Coordinates** by Alice Williams and Dr. Boris Kovalerchuk
- **Interpretable Machine Learning for Self-Service High-Risk Decision-Making** by Charles Recaido and Dr. Boris Kovalerchuk

DCVis is a complete rebuild of the [DSCVis](https://github.com/Charles57-CWU/DSCVis) software, incorporating new visualizations and enhanced tooling.

## Licensing

DCVis is licensed under the MIT License, allowing both personal and commercial use. For full details, please refer to the `LICENSE` file.
