from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QColorDialog
from PyQt6.uic.load_ui import loadUi

import numpy as np

import CLASS_TABLE
import ATTRIBUTE_TABLE
import PLOT
import CLIPPING
import WARNINGS


class View(QtWidgets.QMainWindow):
    def __init__(self, controller=None):
        super(View, self).__init__()

        self.controller: controller = controller
        loadUi('GUI.ui', self)  # load .ui file for GUI made in Qt Designer

        self.plot_widget = None

        self.class_table = None
        self.attribute_table = None

        self.class_pl_exists = True
        self.attribute_pl_exists = True

        self.rule_count = 0

        # for swapping cells
        self.cell_swap = QtWidgets.QTableWidget()
        self.plot_layout = self.findChild(QtWidgets.QVBoxLayout, 'plotDisplay')

    def recenter_plot(self):
        if not self.plot_widget:
            WARNINGS.no_data_warning()
            return

        self.plot_widget.reset_zoom()
        self.plot_widget.resize()

        self.refresh()

    # function to get alpha value for hidden attributes
    def attr_slider(self):
        if not self.controller.data or not self.plot_widget:
            WARNINGS.no_data_warning()
            return
        value = self.attribute_slide.value()
        self.controller.data.attribute_alpha = value
        self.plot_widget.update()

    def check_all_attr(self):
        if not self.controller.data:
            WARNINGS.no_data_warning()
            return
        ATTRIBUTE_TABLE.reset_checkmarks(self.attribute_table, self.controller.data.vertex_count,
                                         self.controller.data.plot_type)

    def check_all_class(self):
        if not self.controller.data:
            WARNINGS.no_data_warning()
            return
        CLASS_TABLE.reset_checkmarks(self.class_table, self.controller.data.class_count)

    def uncheck_all_attr(self):
        if not self.controller.data:
            WARNINGS.no_data_warning()
            return
        ATTRIBUTE_TABLE.uncheck_checkmarks(self.attribute_table, self.controller.data.vertex_count,
                                           self.controller.data.plot_type)

    def uncheck_all_class(self):
        if not self.controller.data:
            WARNINGS.no_data_warning()
            return
        CLASS_TABLE.uncheck_checkmarks(self.class_table, self.controller.data.class_count)

    def keyPressEvent(self, event) -> None:
        if self.plot_widget is None or self.controller.data is None:
            return

        key = event.key()

        if key == QtCore.Qt.Key.Key_Q:
            if self.controller.data.plot_type not in ['SCC', 'DCC']:
                self.controller.data.roll_clips(-1)
            else:
                self.controller.data.roll_vertex_in(-1)
        elif key == QtCore.Qt.Key.Key_E:
            if self.controller.data.plot_type not in ['SCC', 'DCC']:
                self.controller.data.roll_clips(1)
            else:
                self.controller.data.roll_vertex_in(1)

        self.refresh()

    # function to refresh plot
    def refresh(self):
        if self.plot_widget:
            self.plot_widget.update()

    def axes_func(self):
        if not self.controller.data:
            WARNINGS.no_data_warning()
            return

        if self.show_axes.isChecked():
            self.controller.data.axis_on = True
        else:
            self.controller.data.axis_on = False

        self.refresh()

    def create_plot(self):
        if not self.controller.data:
            WARNINGS.no_data_warning()
            return

        # remove initial placeholder
        if self.pl:
            self.plot_layout.removeWidget(self.pl)
        if self.plot_widget:
            self.plot_layout.removeWidget(self.plot_widget)

        self.controller.data.positions = []
        self.controller.data.clipped_samples = np.zeros(self.controller.data.sample_count)
        self.controller.data.clear_samples = np.zeros(self.controller.data.sample_count)
        self.controller.data.vertex_in = np.zeros(self.controller.data.sample_count)
        self.controller.data.last_vertex_in = np.zeros(self.controller.data.sample_count)

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
        elif selected_plot_type == 'Dynamic Circular Coordinates':
            self.controller.data.plot_type = 'DCC'
        else:
            return

        self.plot_widget = PLOT.MakePlot(self.controller.data, parent=self)
        self.remove_clip()  # remove previous clips if any

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
    def analyze_clip(self):
        if not self.plot_widget:
            WARNINGS.no_data_warning()
            return

        CLIPPING.clip_files(self.controller.data, self.clipped_area_textbox)

    def undo_clip(self):
        if not self.plot_widget:
            WARNINGS.no_data_warning()
            return
        self.plot_widget.all_rect.pop()
        if self.rule_count > 0:
            self.rule_count -= 1
            CLIPPING.clip_files(self.controller.data, self.clipped_area_textbox)

        self.plot_widget.update()

    def remove_clip(self):
        if not self.plot_widget:
            WARNINGS.no_data_warning()
            return

        self.controller.data.clipped_samples = np.zeros(self.controller.data.sample_count)
        self.controller.data.clear_samples = np.zeros(self.controller.data.sample_count)
        self.controller.data.vertex_in = np.zeros(self.controller.data.sample_count)
        self.controller.data.last_vertex_in = np.zeros(self.controller.data.sample_count)

        self.plot_widget.all_rect = []

        self.clipped_area_textbox.setText('')

        self.plot_widget.update()

    def hide_clip(self):
        if self.controller.data.plot_type not in ['SCC', 'DCC']:
            self.controller.data.clear_samples = np.add(self.controller.data.clear_samples,
                                                        self.controller.data.clipped_samples)
            self.controller.data.clipped_samples = np.zeros(self.controller.data.sample_count)
        else:
            self.controller.data.clear_samples = np.add(self.controller.data.clear_samples,
                                                        self.controller.data.vertex_in)
            self.controller.data.clipped_samples = np.zeros(self.controller.data.sample_count)
        self.rule_count += 1
        current_rule_coords = self.plot_widget.all_rect[self.rule_count - 1]
        formatted_coords = [round(num, 2) for num in current_rule_coords]
        self.rules_textbox.append('\nRule ' + str(self.rule_count) + ' : ' + str(formatted_coords))

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
            WARNINGS.no_data_warning()
            return

        self.controller.data.attribute_names.append('class')
        self.controller.data.dataframe = self.controller.data.dataframe[self.controller.data.attribute_names]

        self.controller.data.attribute_names.pop()
        self.controller.data.positions = []
        self.controller.data.active_attributes = np.repeat(True, self.controller.data.attribute_count)
        ATTRIBUTE_TABLE.reset_checkmarks(self.attribute_table, self.controller.data.vertex_count,
                                         self.controller.data.plot_type)

        self.create_plot()

    def open_background_color_picker(self):
        if not self.plot_widget:
            WARNINGS.no_data_warning()
            return
        color = QColorDialog.getColor()
        if color.isValid():
            self.background_color = [color.redF(), color.greenF(), color.blueF(), color.alphaF()]
            self.plot_widget.redraw_plot(background_color=self.background_color)

    def open_axes_color_picker(self):
        if not self.plot_widget:
            WARNINGS.no_data_warning()
            return
        color = QColorDialog.getColor()
        if color.isValid():
            self.axes_color = [color.redF(), color.greenF(), color.blueF(), color.alphaF()]
            self.plot_widget.redraw_plot(axes_color=self.axes_color)
