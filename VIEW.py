from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QColorDialog
from PyQt6.uic.load_ui import loadUi

import numpy as np

import CLASS_TABLE, ATTRIBUTE_TABLE, PLOT, CLIPPING,WARNINGS


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
        ATTRIBUTE_TABLE.reset_checkmarks(self.attribute_table, self.controller.data.vertex_count, self.controller.data.plot_type)

    def check_all_class(self):
        if not self.controller.data:
            WARNINGS.no_data_warning()
            return
        CLASS_TABLE.reset_checkmarks(self.class_table, self.controller.data.class_count)

    def uncheck_all_attr(self):
        if not self.controller.data:
            WARNINGS.no_data_warning()
            return
        ATTRIBUTE_TABLE.uncheck_checkmarks(self.attribute_table, self.controller.data.vertex_count, self.controller.data.plot_type)

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
        # Check if data not loaded
        if not (hasattr(self, 'controller') and self.controller is not None and self.controller.data is not None):
            WARNINGS.no_data_warning()
            return
        # Check if data load was cancelled
        if not (self.controller.data and self.controller.data.class_count > 0):
            print("No class data available to display in ClassTable.")
            return
        
        self.rules_textbox.setText('')
        self.overlaps_textbox.setText('')
        self.controller.data.overlap_count = 0

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

        self.plot_widget = PLOT.Plot(self.controller.data, self.overlaps_textbox, self.controller.view.replot_overlaps_btn, parent=self)
        self.remove_clips()

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
        
        if self.class_table:
            self.class_table_layout.removeWidget(self.class_table)
        
        self.controller.view.class_table = CLASS_TABLE.ClassTable(self.controller.data, parent=self)
        self.class_table_layout.addWidget(self.controller.view.class_table)
        
    def analyze_clip(self):
        if not self.plot_widget:
            WARNINGS.no_data_warning()
            return
        
        if len(self.plot_widget.all_rect) == 0:
            self.clipped_area_textbox.setText('No clipping area selected.')
            return
        CLIPPING.clip_files(self.controller.data, self.clipped_area_textbox)

    def undo_clip(self):
        if not self.plot_widget:
            WARNINGS.no_data_warning()
            return

        # Ensure there is at least one rectangle to remove
        if self.plot_widget.all_rect:
            # Remove the last rectangle
            self.plot_widget.all_rect.pop()

            # Reset the clipping-related attributes before recalculating
            self.controller.data.clipped_samples = np.zeros(self.controller.data.sample_count)
            self.controller.data.vertex_in = np.zeros(self.controller.data.sample_count)
            self.controller.data.last_vertex_in = np.zeros(self.controller.data.sample_count)

            # Recalculate clipping for the remaining rectangles
            for rect in self.plot_widget.all_rect:
                positions = self.controller.data.positions
                CLIPPING.Clipping(rect, self.controller.data)
                CLIPPING.clip_samples(positions, rect, self.controller.data)

            # Update rule count if necessary
            if self.rule_count > 0:
                self.rule_count -= 1

            self.clipped_area_textbox.setText('')

            self.plot_widget.update()
        else:
            print("No rectangles to remove.")

    def remove_clips(self):
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
        
        return

    def hide_clip(self):
        if self.controller.data.plot_type not in ['SCC', 'DCC']:
            self.controller.data.clear_samples = np.add(self.controller.data.clear_samples, self.controller.data.clipped_samples)
            self.controller.data.clipped_samples = np.zeros(self.controller.data.sample_count)
        else:
            self.controller.data.clear_samples = np.add(self.controller.data.clear_samples, self.controller.data.vertex_in)
            self.controller.data.clipped_samples = np.zeros(self.controller.data.sample_count)

    def remove_rules(self):
        self.rule_count = 0
        
        self.controller.data.rule_regions = {}
        self.rules_textbox.setText('')
        
        self.plot_widget.update()

    def trace_mode_func(self):
        self.controller.data.trace_mode = not self.controller.data.trace_mode
        self.plot_widget.update()

    def add_rule(self):
        if not self.plot_widget.all_rect:
            print("No clipping area selected.")
            return

        rules = self.plot_widget.all_rect
        
        primary_class = CLIPPING.primary_clipped_class(self.controller.data)
        if CLIPPING.is_pure_class(self.controller.data):
            primary_class += " (pure)"
        if primary_class in self.controller.data.rule_regions:
            self.controller.data.rule_regions[primary_class] += rules
        else:
            self.controller.data.rule_regions[primary_class] = rules      
        class_name_or_false = CLIPPING.count_clipped_classes(self.controller.data)

        if not class_name_or_false:
            rule_description = f"Rule {self.rule_count + 1}: {rules} is not pure"
        else:
            rule_description = f"Rule {self.rule_count + 1}: {rules} contains classes: {class_name_or_false}"
        
        self.rule_count += 1
        self.rules_textbox.append(rule_description)
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
        ATTRIBUTE_TABLE.reset_checkmarks(self.attribute_table, self.controller.data.vertex_count, self.controller.data.plot_type)
        if self.attribute_table:
            self.attribute_table.clearTableWidgets()
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

    def replot_overlaps(self):
        if not self.plot_widget:
            WARNINGS.no_data_warning()
            return
        self.plot_widget.replot_overlaps()
