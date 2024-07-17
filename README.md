# DCVis: Dynamic Coordinate Visualization System

DCVis is software for Visual Knowledge Discovery (VKD) developed at Central Washington University's Visual Knowledge Discovery Lab. Initiated in 2022, the project is built by Alice Williams, James Battistoni IV, Charles Recaido, and Dr. Boris Kovalerchuk.

DCVis allows users to interactively build visual ML models for classifying new data. It offers tools to explore multidimensional data using General Line Coordinate visualizations and includes features for interactive classification and synthetic data generation to enhance supervised learning models.

## Requirements

- Python 3.x: Recommended version 3.6 or higher (primarily developed on Python 3.10.6).
- Dependencies: Install libraries from requirements.txt by running `pip install -r requirements.txt` in the terminal.

## Setup

To set up the project:

1. **Download the project and open it in a terminal:**
   - Use git to download and open in an IDE with an integrated terminal.
2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   ```
   (The virtual environment will be named `venv`)
3. **Activate the virtual environment:**
   (Refer to the table below for your OS and shell)
4. **Install the required libraries:**
   ```sh
   python -m pip install -r requirements.txt
   ```
5. **Start the application:**
   ```sh
   python DCVIS_MAIN.py
   ```

| Platform   | Shell     | Command to activate virtual environment |
|------------|-----------|-----------------------------------------|
| POSIX      | bash/zsh  | `$ source <venv>/bin/activate`          |
|            | fish      | `$ source <venv>/bin/activate.fish`     |
|            | csh/tcsh  | `$ source <venv>/bin/activate.csh`      |
| PowerShell |           | `$ <venv>/bin/Activate.ps1`             |
| Windows    | cmd.exe   | `C:\> <venv>\Scripts\activate.bat`      |
|            | PowerShell| `PS C:\> <venv>\Scripts\Activate.ps1`   |

Source: [Python Virtual Environments Documentation](https://docs.python.org/3/library/venv.html)

## Running

Execute the `DCVIS_MAIN.py` script to launch the DCVis application:
```sh
python DCVIS_MAIN.py
```

## Software Features

DCVis offers tools for visualizing and analyzing multidimensional numerical data:

## Visualization Capabilities

- **2D Visualizations**: Use OpenGL to render multidimensional data from .csv or .txt files.
- **Interactive Plotting**: Pan, zoom, and adjust color/transparency options.
- **Dynamic Visualization**: Reorder or invert axes to uncover patterns in n-D data.

## Data Interaction

- **Clipping Tools**: Dual-right click to highlight, analyze, export, or hide data.
- **Point Selection**: Select points directly on the plot for detailed examination.

## Classification and Analysis

- **Rule-Based Classification**: Create and combine classification rules to build visual ML models.
- **Enhanced Learning Models**: Use interactive tools and synthetic data generation to improve supervised learning classifiers.

## Customization

- **Configurable Display**: Customize background, class, and axes colors.
- **Visibility Toggles**: Show or hide axes, points, and other elements.
- **Trace Mode**: Use alternating colors to trace data points across visualization schemes.

## User Interface Enhancements

- **Interactive UI Elements**: Manage data and visualization settings with intuitive controls.
- **Hotkeys and Shortcuts**: Access frequently used functions with keyboard shortcuts.

These features provide an interactive, user-friendly experience for data analysis.

## Mouse Interactions

- **Pan Plot**: Click and drag with the scroll-wheel.
- **Zoom**: Scroll the mouse wheel.
- **Box Clipping**: Right-click twice to create a clipping rectangle.
- **Select Point**: Left-click to select single or multiple points.
- **Grow Clipping Box**: Middle-click once to create clipping box, again to grow it.

## Keyboard Shortcuts

- **Cycle Selections**: `Q` and `E` keys.
- **Adjust Vertical Position**: `W` and `S` keys.
- **Delete Samples**: `D` key.
- **Print Samples**: `P` key.
- **Clone Samples**: `C` key.
- **Insert Sample**: `I` key.

## UI Elements

- **Highlight Clipped Cases**: Clipped cases are highlighted; use 'Add Classification Rule' to convert to a new rule.
- **Rule Visibility**: Toggle visibility with the checkbox next to the rule.
- **Reorder Tables**: Drag and drop within class and attribute tables.
- **Adjust Transparency**: Use the slider below the attribute table.

## Datasets Included

| Dataset                       | Cases  | Features | Classes |
|-------------------------------|--------|----------|---------|
| Fisher Iris                   | 150    | 4        | 3       |
| WBC (Original)                | 696    | 9        | 2       |
| WBC (Wisconsin Breast Cancer) | 569    | 30       | 2       |
| Diabetes                      | 768    | 8        | 2       |
| Heart Disease                 | 1,025  | 13       | 2       |
| Ionosphere                    | 351    | 34       | 2       |
| MNIST Capital Letters         | 20,000 | 16       | 26      |
| Sinusoidal Wave               | 200    | 2        | 2       |
| Wheat Seed                    | 210    | 7        | 3       |
| Wine                          | 4,898  | 11       | 7       |

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

DCVis is a complete rebuild of the [DSCVis](https://github.com/Charles57-CWU/DSCVis) software, with new visualizations and enhanced tools.

## Licensing

DCVis is licensed under the MIT License, allowing both personal and commercial use. For full details, see the `LICENSE` file.
