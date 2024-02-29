from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
import DATA_DISPLAY
import DATASET
import sys

import CLASS_TABLE


class Controller:
    def __init__(self, view, dataset=None):
        self.data = dataset
        self.view = view
        if self.view is not None:
            self.setup_connections()

    def setup_connections(self):
        self.view.load_button.clicked.connect(self.load_dataset)
        self.view.load_button.setShortcut(Qt.Key.Key_F1)
        self.view.plot_button.clicked.connect(self.view.create_plot)
        self.view.plot_button.setShortcut(Qt.Key.Key_F3)
        self.view.exit_button.clicked.connect(lambda: sys.exit())
        self.view.exit_button.setShortcut(Qt.Key.Key_Escape)
        self.view.actionExit.triggered.connect(lambda: sys.exit())
        self.view.analyze_clip_button.clicked.connect(self.view.analyze_clip)
        self.view.hide_clip_button.clicked.connect(self.view.hide_clip)
        self.view.undo_clip_button.clicked.connect(self.view.undo_clip)
        self.view.remove_clip_button.clicked.connect(self.view.remove_clip)
        self.view.recenter_button.clicked.connect(self.view.recenter_plot)
        self.view.recenter_button.setShortcut(Qt.Key.Key_F2)
        self.view.show_axes.stateChanged.connect(self.view.axes_func)
        self.view.attribute_slide.valueChanged.connect(self.view.attr_slider)
        self.view.check_classes.clicked.connect(self.view.check_all_class)
        self.view.uncheck_classes.clicked.connect(self.view.uncheck_all_class)
        self.view.check_attributes.clicked.connect(self.view.check_all_attr)
        self.view.uncheck_attributes.clicked.connect(self.view.uncheck_all_attr)
        self.view.cell_swap.__class__.dropEvent = self.view.table_swap
        self.view.background_button.clicked.connect(self.view.open_background_color_picker)
        self.view.axes_button.clicked.connect(self.view.open_axes_color_picker)

    def load_dataset(self):
        if self.data:
            del self.data

        self.data = DATASET.Dataset()
        filename = QtWidgets.QFileDialog.getOpenFileName(self.view, 'Open File', 'datasets')
        if filename[0] == '':
            return

        # GUI changes for changing datasets
        if self.data and self.view.plot_widget and self.view.class_table and self.view.plot_layout:
            self.view.plot_layout.removeWidget(self.view.plot_widget)
            del self.view.plot_widget
            self.view.plot_widget = None
            self.view.plot_layout.addWidget(self.view.pl)

            self.view.class_table_layout.removeWidget(self.view.class_table)
            del self.view.class_table
            self.view.class_table = None
            self.view.class_table_layout.addWidget(self.view.class_pl)
            self.view.class_pl_exists = True

            self.view.attribute_table_layout.removeWidget(self.view.attribute_table)
            del self.view.attribute_table
            self.view.attribute_table = None
            self.view.attribute_table_layout.addWidget(self.view.attribute_pl)
            self.view.attribute_pl_exists = True

        self.data.load_from_csv(filename[0])
        DATA_DISPLAY.DisplayData(self.data, self.view.dataset_textbox)
        self.view.class_table = CLASS_TABLE.ClassTable(self.data, parent=self.view)

