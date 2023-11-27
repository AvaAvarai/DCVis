from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

def table_swap(table, dataset, event, replot_func):
    moved_from = table.currentRow()
    from_item = table.item(moved_from, 0)
    if from_item == None:  # if no item is selected
        return
    from_item = from_item.text()
    moved_to = table.rowAt(round(event.position().y()))

    to_item = table.item(moved_to, 0)
    if to_item == None:  # if no item is selected
        return
    to_item = to_item.text()

    table.item(moved_from, 0).setText(to_item)
    table.item(moved_to, 0).setText(from_item)

    place_holder = dataset.attribute_names[moved_from]
    dataset.attribute_names[moved_from] = dataset.attribute_names[moved_to]
    dataset.attribute_names[moved_to] = place_holder

    place_holder = dataset.attribute_order[moved_from]
    dataset.attribute_order[moved_from] = dataset.attribute_order[moved_to]
    dataset.attribute_order[moved_to] = place_holder

    place_holder = dataset.active_attributes[moved_from]
    dataset.active_attributes[moved_from] = dataset.active_attributes[moved_to]
    dataset.active_attributes[moved_to] = place_holder
    
    replot_func()

def reset_checkmarks(table, count, plot_type):
    for idx in range(count):
        if plot_type == 'SPC' or plot_type == 'DSC2':
            cell = table.cellWidget(idx*2, 1)
            cell.setCheckState(Qt.CheckState.Checked)
        else:
            cell = table.cellWidget(idx, 1)
            cell.setCheckState(Qt.CheckState.Checked)

def uncheck_checkmarks(table, count, plot_type):
    for idx in range(count):
        if plot_type == 'SPC' or plot_type == 'DSC2':
            cell = table.cellWidget(idx*2, 1)
            cell.setCheckState(Qt.CheckState.Unchecked)
        else:
            cell = table.cellWidget(idx, 1)
            cell.setCheckState(Qt.CheckState.Unchecked)

class AttributeTable(QtWidgets.QTableWidget):
    def __init__(self, dataset, replot_func, parent=None):
        super(AttributeTable, self).__init__(parent)

        self.dataset = dataset
        self.replot_func = replot_func

        self.setRowCount(self.dataset.attribute_count)
        self.setColumnCount(3)  # Add an extra column for the toggle buttons

        # Set header labels for the new column
        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Attribute Order'))
        self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Transparency'))
        self.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem('Invert'))

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)

        for idx, attribute_name in enumerate(self.dataset.attribute_names):
            self.setItem(idx, 0, QtWidgets.QTableWidgetItem(attribute_name))

            transparency_checkbox = CheckBox(idx, self.dataset, 'transparency', parent=self)
            self.setCellWidget(idx, 1, transparency_checkbox)

            # Add a toggle button for inversion
            inversion_checkbox = InversionCheckBox(idx, self.dataset, self.replot_func, parent=self)
            self.setCellWidget(idx, 2, inversion_checkbox)

class CheckBox(QtWidgets.QCheckBox):
    def __init__(self, row, dataset, option, parent=None):
        super(CheckBox, self).__init__(parent)
        self.index = row
        self.data = dataset
        self.option = option
        self.setCheckState(Qt.CheckState.Checked)
        self.stateChanged.connect(self.show_hide_classes)

    def show_hide_classes(self):
        if self.isChecked():
            if self.data.plot_type == 'SPC' or self.data.plot_type == 'DSC2':
                self.data.active_attributes[int(self.index / 2)] = True
            else:
                self.data.active_attributes[self.index] = True
        else:
            if self.data.plot_type == 'SPC' or self.data.plot_type == 'DSC2':
                self.data.active_attributes[int(self.index / 2)] = False
            else:
                self.data.active_attributes[self.index] = False

class InversionCheckBox(QtWidgets.QCheckBox):
    def __init__(self, index, dataset, replot_func, parent=None):
        super(InversionCheckBox, self).__init__(parent)
        self.index = index
        self.dataset = dataset
        self.replot_func = replot_func

        # Initialize the checkbox state based on the attribute_inversions list
        self.setChecked(self.dataset.attribute_inversions[self.index])

        # Connect the stateChanged signal to the toggle_inversion method
        self.stateChanged.connect(self.toggle_inversion)

    def toggle_inversion(self, state):
        # Update the attribute_inversions list with the new state
        # We use `not state` because the inversion list is meant to be True when not inverted
        self.dataset.attribute_inversions[self.index] = not self.dataset.attribute_inversions[self.index]
        self.replot_func()
