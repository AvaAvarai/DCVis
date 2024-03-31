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
        self.cell_swap = QtWidgets.QTableWidget()
        self.plot_layout = self.findChild(QtWidgets.QVBoxLayout, 'plotDisplay')

        # Setup context menu for rulesListWidget
        self.rulesListWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.rulesListWidget.customContextMenuRequested.connect(self.openContextMenu)
        
        self.rulesListWidget.itemClicked.connect(self.highlightAssociatedRegions)
    
    def highlightAssociatedRegions(self, item):
        rule_num = item.text().split()[1][:-1]
        rule_num = int(rule_num) - 1
        rules = self.controller.data.rule_regions
        if rule_num in rules:
            rule = rules[rule_num]
            primary_class, rects = rule
            
            # Check if it's already highlighted or not
            if not primary_class.endswith(" (highlighted)"):
                # Mark as highlighted
                new_primary_class = primary_class + " (highlighted)"
            else:
                # Remove "(highlighted)" to toggle off the highlight
                new_primary_class = primary_class[:-14]
            
            # Update the rule with the new primary class name
            self.controller.data.rule_regions[rule_num] = (new_primary_class, rects)
            self.plot_widget.update()
                
    def removeSelectedRule(self):
        currentItem = self.rulesListWidget.currentItem()
        if currentItem:
            row = self.rulesListWidget.row(currentItem)
            item = self.rulesListWidget.takeItem(row)

            item_text = item.text()
            item_num = int(item_text.split()[1][:-1]) - 1

            if not item_num in self.controller.data.rule_regions:
                return
            
            self.controller.data.rule_regions.pop(item_num)

            
            self.controller.data.clear_samples = np.zeros(self.controller.data.sample_count)
            # clip remaining rules and update clear_samples
            for rule in self.controller.data.rule_regions.values():
                for rect in rule[1]:
                    positions = self.controller.data.positions
                    CLIPPING.Clipping(rect, self.controller.data)
                    CLIPPING.clip_samples(positions, rect, self.controller.data)
            self.controller.data.clear_samples = np.add(self.controller.data.clear_samples, self.controller.data.clipped_samples)
            self.rule_count -= 1
            del item
            self.plot_widget.update()
            
    def openContextMenu(self, position):
        menu = QtWidgets.QMenu()
        removeAction = menu.addAction("Remove Rule")
        action = menu.exec(self.rulesListWidget.mapToGlobal(position))
        if action == removeAction:
            self.removeSelectedRule()

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
        
        self.rulesListWidget.clear()
        self.controller.data.rule_regions = {}
        self.rule_count = 0
        self.controller.data.rule_count = 0
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

            self.clipped_area_textbox.clear()

            self.plot_widget.update()
        else:
            print("No rectangles to remove.")

    def remove_clips(self):
        if not self.plot_widget:
            WARNINGS.no_data_warning()
            return

        self.controller.data.clipped_samples = np.zeros(self.controller.data.sample_count)
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
        self.controller.data.clear_samples = np.zeros(self.controller.data.sample_count)
        
        self.rulesListWidget.clear()
        
        self.plot_widget.update()

    def trace_mode_func(self):
        self.controller.data.trace_mode = not self.controller.data.trace_mode
        self.plot_widget.update()

    def add_rule(self):
        if not self.plot_widget.all_rect:
            print("No clipping area selected.")
            return

        rules = self.plot_widget.all_rect
        
        skips = []
        for i, _ in enumerate(self.controller.data.clear_samples):
            if self.controller.data.clear_samples[i] == 1:
                skips.append(i)
        class_set = CLIPPING.count_clipped_classes(self.controller.data, skips)
        if len(class_set) == 1:
            class_add = class_set.pop()
            primary_class = class_add  + " (pure)"
            class_set.add(class_add)
        else:
            primary_class = CLIPPING.primary_clipped_class(self.controller.data)
        if primary_class in self.controller.data.rule_regions:
            primary_class += f" ({self.controller.data.rule_count})"
        else:
            self.controller.data.rule_regions[self.rule_count] = (primary_class, rules)
        
        class_str = ""
        for index, c in enumerate(class_set):
            class_str += c
            if index < len(class_set) - 1:
                class_str += ", "
        
        # count number of samples clipped by rule which are in clear_samples
        overcounts = np.count_nonzero(np.logical_and(self.controller.data.clipped_samples, self.controller.data.clear_samples))
        
        case_count = CLIPPING.count_clipped_samples(self.controller.data)

        case_count -= overcounts
        class_count = len(class_set)

        if class_count == 1:
            class_str += " class"
        else:
            class_str += " classes"
        
        cases_str = ""
        if case_count == 1:
            cases_str = "case"
        else:
            cases_str = "cases"
        
        region_str = ""
        if len(rules) == 1:
            region_str = "region"
        else:
            region_str = "regions"
        
        rule_description = f"Rule {self.rule_count + 1}) {case_count} {cases_str} {class_str} {len(rules)} {region_str}"
        
        item = QtWidgets.QListWidgetItem(rule_description)
        item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(QtCore.Qt.CheckState.Checked)

        self.rulesListWidget.addItem(item)
        self.rulesListWidget.itemChanged.connect(self.onRuleItemChanged)

        self.rule_count += 1
        
        self.plot_widget.update()

    def onRuleItemChanged(self, item):
        # Check if the item's checkbox is checked
        if item.checkState() == QtCore.Qt.CheckState.Checked:
            rule_num = item.text().split()[1][:-1]
            rule_num = int(rule_num) - 1
            rules = self.controller.data.rule_regions
            rule = rules[list(rules.keys())[rule_num]]
            for rect in rule[1]:
                positions = self.controller.data.positions
                CLIPPING.Clipping(rect, self.controller.data)
                CLIPPING.clip_samples(positions, rect, self.controller.data)
            
            self.controller.data.clear_samples = np.subtract(self.controller.data.clear_samples, self.controller.data.clipped_samples)
            self.controller.data.clipped_samples = np.zeros(self.controller.data.sample_count)
        else:
            rule_num = item.text().split()[1][:-1]
            rule_num = int(rule_num) - 1
            rules = self.controller.data.rule_regions
            if len(rules) > rule_num:
                rule = rules[list(rules.keys())[rule_num]]
                for rect in rule[1]:
                    positions = self.controller.data.positions
                    CLIPPING.Clipping(rect, self.controller.data)
                    CLIPPING.clip_samples(positions, rect, self.controller.data)
                self.controller.data.clear_samples = np.add(self.controller.data.clear_samples, self.controller.data.clipped_samples)
                self.controller.data.clipped_samples = np.zeros(self.controller.data.sample_count)
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
