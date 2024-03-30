"""
DCVis - Dynamic Coordinate Visualization System

Requirements:
- Python 3.x: Recommended Python 3.6 or higher for compatibility.
- Libraries installed from requirements.txt: Use pip to install the required libraries. Run the following command in the terminal: pip install -r requirements.txt

Usage:
Execute this script to launch the DCVis application: python DCVIS_MAIN.py

Project contributors: Alice Williams, James Battistoni, Charles Recaido, and Dr. Boris Kovalerchuk
at Central Washington University Visual Knowledge Discovery Lab, project during years 2022 to 2024.

Available under the MIT License, allowing for both personal and commercial use.
"""

from PyQt6 import QtWidgets
import sys
import VIEW, CONTROLLER
  

# DCVis application entry point
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    view = VIEW.View()
    controller = CONTROLLER.Controller(view)
    view.controller = controller

    view.show()
    app.exec()
