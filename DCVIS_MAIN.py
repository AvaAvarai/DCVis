from PyQt6 import QtWidgets

import sys

import VIEW
import CONTROLLER


# DCVis application entry point
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    view = VIEW.View()
    
    controller = CONTROLLER.Controller(view)
    view.controller = controller

    view.show()
    app.exec()

