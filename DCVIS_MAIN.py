from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QColorDialog
from PyQt6.QtCore import Qt
from PyQt6.uic.load_ui import loadUi
import numpy as np
import sys

import DATA_DISPLAY
import CLASS_TABLE
import ATTRIBUTE_TABLE
import PLOT
import CLIPPING
import WARNINGS
import DATASET

class UiView(QtWidgets.QMainWindow):
    def __init__(self, controller=None):
        super(UiView, self).__init__()
        
        self.controller: controller = controller
        loadUi('GUI.ui', self)  # load .ui file for GUI made in Qt Designer

        self.plot_widget = None

        self.class_table = None
        self.attribute_table = None
        
        self.class_pl_exists = True
        self.attribute_pl_exists = True

        # for swapping cells
        self.cell_swap = QtWidgets.QTableWidget()
        self.plot_layout = self.findChild(QtWidgets.QVBoxLayout, 'plotDisplay')

    def recenter_plot(self):
        if not self.plot_widget:
            WARNINGS.noDataWarning()
            return
        # for zooming
        self.plot_widget.m_left = -1.125
        self.plot_widget.m_right = 1.125
        self.plot_widget.m_bottom = -1.125
        self.plot_widget.m_top = 1.125
        
        if self.controller.data.plot_type == 'SCC':  # fit CC to window
            self.plot_widget.m_left = -self.controller.data.attribute_count * 0.5
            self.plot_widget.m_right = self.controller.data.attribute_count * 0.5
            self.plot_widget.m_bottom = -self.controller.data.attribute_count * 0.5
            self.plot_widget.m_top = self.controller.data.attribute_count * 0.5

        self.refresh()

    # function to get alpha value for hidden attributes
    def attr_slider(self):
        if not self.controller.data or not self.plot_widget:
            WARNINGS.noDataWarning()
            return
        value = self.attribute_slide.value()
        self.controller.data.attribute_alpha = value
        self.plot_widget.update()

    def check_all_attr(self):
        if not self.controller.data:
            WARNINGS.noDataWarning()
            return
        ATTRIBUTE_TABLE.reset_checkmarks(self.attribute_table, self.controller.data.vertex_count, self.controller.data.plot_type)

    def check_all_class(self):
        if not self.controller.data:
            WARNINGS.noDataWarning()
            return
        CLASS_TABLE.reset_checkmarks(self.class_table, self.controller.data.class_count)

    def uncheck_all_attr(self):
        if not self.controller.data:
            WARNINGS.noDataWarning()
            return
        ATTRIBUTE_TABLE.uncheck_checkmarks(self.attribute_table, self.controller.data.vertex_count, self.controller.data.plot_type)

    def uncheck_all_class(self):
        if not self.controller.data:
            WARNINGS.noDataWarning()
            return
        CLASS_TABLE.uncheck_checkmarks(self.class_table, self.controller.data.class_count)

    # function to refresh plot
    def refresh(self):
        if self.plot_widget:
            self.plot_widget.update()

    def axes_func(self):
        if not self.controller.data:
            WARNINGS.noDataWarning()
            return

        if self.show_axes.isChecked():
            self.controller.data.axis_on = True
        else:
            self.controller.data.axis_on = False

        self.refresh()

    def create_plot(self):
        if not self.controller.data:
            WARNINGS.noDataWarning()
            return

        # remove initial placeholder
        if self.pl:
            self.plot_layout.removeWidget(self.pl)
        if self.plot_widget:
            self.plot_layout.removeWidget(self.plot_widget)

        self.controller.data.positions = []
        
        selected_plot_type = self.plot_select.currentText()
        
        if selected_plot_type == 'Parallel Coordinates':
            self.controller.data.plot_type = 'PC'
        elif selected_plot_type == 'Dynamic Scaffold Coordinates 1':
            self.controller.data.plot_type = 'DSC1'
        elif selected_plot_type == 'Dynamic Scaffold Coordinates 2':
            self.controller.data.plot_type = 'DSC2'
        elif selected_plot_type == 'Shifted Paired Coordinates':
            self.controller.data.plot_type = 'SPC'
        elif selected_plot_type == 'Static Circular Coordinates':
            self.controller.data.plot_type = 'SCC'
        else:
            return
        
        self.plot_widget = PLOT.MakePlot(self.controller.data, parent=self)

        # class table placeholder
        if self.class_pl_exists:
            self.class_table_layout.removeWidget(self.class_pl)
            self.class_table_layout.addWidget(self.class_table)
            self.class_pl_exists = False

        # attribute table placeholder
        if self.attribute_pl_exists:
            self.attribute_table_layout.removeWidget(self.attribute_pl)
            self.attribute_pl_exists = False
        else:
            self.attribute_table_layout.removeWidget(self.attribute_table)

        self.attribute_table = ATTRIBUTE_TABLE.AttributeTable(self.controller.data, self.replot_attributes, parent=self)
        self.attribute_table_layout.addWidget(self.attribute_table)

        self.plot_layout.addWidget(self.plot_widget)

    # function to save clip files
    def test(self):
        if not self.plot_widget:
            WARNINGS.noDataWarning()
            return

        CLIPPING.clip_files(self.controller.data, self.clipped_area_textbox)

    def remove_clip(self):
        if not self.plot_widget:
            WARNINGS.noDataWarning()
            return
        
        self.controller.data.clipped_samples = np.zeros(self.controller.data.sample_count)
        self.controller.data.vertex_in = np.zeros(self.controller.data.sample_count)
        self.controller.data.last_vertex_in = np.zeros(self.controller.data.sample_count)
        self.plot_widget.all_rect = []

        self.clipped_area_textbox.setText('')

        self.plot_widget.update()

    def table_swap(self, event):
        table = event.source()

        if table == self.class_table:
            CLASS_TABLE.table_swap(table, self.controller.data, self.plot_widget, event)
        elif table == self.attribute_table:
            ATTRIBUTE_TABLE.table_swap(table, self.controller.data, event, self.replot_attributes)

        event.accept()

    def replot_attributes(self):
        if not self.plot_widget:
            WARNINGS.noDataWarning()
            return
        
        self.controller.data.attribute_names.append('class')
        self.controller.data.dataframe = self.controller.data.dataframe[self.controller.data.attribute_names]

        self.controller.data.attribute_names.pop()
        self.controller.data.positions = []
        self.controller.data.active_attributes = np.repeat(True, self.controller.data.attribute_count)
        ATTRIBUTE_TABLE.reset_checkmarks(self.attribute_table, self.controller.data.vertex_count, self.controller.data.plot_type)
        
        self.create_plot()

    def open_background_color_picker(self):
        if not self.plot_widget:
            WARNINGS.noDataWarning()
            return
        color = QColorDialog.getColor()
        if color.isValid():
            self.background_color = [color.redF(), color.greenF(), color.blueF(), color.alphaF()]
            self.plot_widget.redraw_plot(background_color=self.background_color)

    def open_axes_color_picker(self):
        if not self.plot_widget:
            WARNINGS.noDataWarning()
            return
        color = QColorDialog.getColor()
        if color.isValid():
            self.axes_color = [color.redF(), color.greenF(), color.blueF(), color.alphaF()]
            self.plot_widget.redraw_plot(axes_color=self.axes_color)


class MainController:
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
        self.view.test_button.clicked.connect(self.view.test)
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


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    main_view = UiView()
    
    main_controller = MainController(main_view)
    main_view.controller = main_controller

    main_view.show()
    app.exec()
