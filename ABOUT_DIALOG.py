from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Information")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        about_info = """
            Dynamic Coordinates Visualisation System
            A General Line Coordinates (GLC) system for Visual Knowledge Discovery (VKD),
            Our system is designed to support:
              multidimensional data visualization
              data classification
              data mining
              synthetic data generation
        
        Please see the README.md file for more information.
        
        If you encounter any problems please let us known through our Github issues page, thank you!
        """
        
        label = QLabel(about_info)
        layout.addWidget(label)
        button = QPushButton("Close", clicked=self.accept)
        layout.addWidget(button)
        
        self.setLayout(layout)
