from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Control Help")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        controls_info = """
        DCVis Controls Help
        
        Keyboard Shortcuts:
        F1: Load Dataset
        F2: Recenter Plot
        F3: Create Plot
        F4: Refresh Plot
        ESC: Exit Application
        
        Mouse Controls:
        Left Click: Select and highlight data points.
        Right Click: Set clipping boundaries or clear data.
        Middle Click and Drag: Pan the plot.
        Scroll Wheel: Zoom in and out on the plot.
        
        All other controls are available through the GUI.
        Please see the README.md file for more information.
        """
        label = QLabel(controls_info)
        layout.addWidget(label)
        button = QPushButton("Close", clicked=self.accept)
        layout.addWidget(button)
        self.setLayout(layout)
