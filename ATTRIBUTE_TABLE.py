from PyQt6 import QtWidgets, QtCore, QtGui
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
            cell = table.cellWidget(idx * 2, 1)
            cell.setCheckState(Qt.CheckState.Checked)
        else:
            cell = table.cellWidget(idx, 1)
            cell.setCheckState(Qt.CheckState.Checked)


def uncheck_checkmarks(table, count, plot_type):
    for idx in range(count):
        if plot_type == 'SPC' or plot_type == 'DSC2':
            cell = table.cellWidget(idx * 2, 1)
            cell.setCheckState(Qt.CheckState.Unchecked)
        else:
            cell = table.cellWidget(idx, 1)
            cell.setCheckState(Qt.CheckState.Unchecked)


class AttributeTable(QtWidgets.QTableWidget):
    def __init__(self, dataset, replot_func, parent=None):
        super(AttributeTable, self).__init__(parent)

        self.dataset = dataset
        self.replot_func = replot_func

        if self.dataset.plot_type == 'DCC':
            self.setColumnCount(2)  # Adjusted for coefficient slider and textbox
            self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Coefficient Slider'))
            self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Value'))
        else:
            self.setColumnCount(3)  # Original setup
            self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Attribute Order'))
            self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Transparency'))
            self.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem('Invert'))

        self.setRowCount(self.dataset.attribute_count)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)

        if self.dataset.plot_type == 'DCC':
            for idx in range(self.dataset.attribute_count):
                self.initDccRow(idx)
        else:
            for idx, attribute_name in enumerate(self.dataset.attribute_names):
                self.setItem(idx, 0, QtWidgets.QTableWidgetItem(attribute_name))
                self.setCellWidget(idx, 1, CheckBox(idx, self.dataset, 'transparency', parent=self))
                self.setCellWidget(idx, 2, InversionCheckBox(idx, self.dataset, self.replot_func, parent=self))

    def initDccRow(self, idx):
        # Initialize slider
        slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(int(self.dataset.coefs[idx]))  # Assuming coefs are initially set to 100
        slider.valueChanged.connect(lambda value, x=idx: self.updateTextBox(x, value))

        # Initialize textbox
        textbox = QtWidgets.QLineEdit()
        textbox.setText(str(int(self.dataset.coefs[idx])))
        textbox.setValidator(QtGui.QIntValidator(0, 100))
        textbox.textChanged.connect(lambda value, x=idx: self.updateSlider(x, value))

        self.setCellWidget(idx, 0, slider)
        self.setCellWidget(idx, 1, textbox)

    def updateSlider(self, idx, value):
        if value:
            self.cellWidget(idx, 0).setValue(int(value))
            self.dataset.update_coef(idx, int(value))

    def updateTextBox(self, idx, value):
        self.cellWidget(idx, 1).setText(str(value))
        self.dataset.update_coef(idx, value)

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
