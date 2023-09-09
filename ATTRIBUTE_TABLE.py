from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

def table_swap(table, dataset, event):
    moved_from = table.currentRow()
    from_item = table.item(moved_from, 0).text()
    moved_to = table.rowAt(round(event.position().y()))
    to_item = table.item(moved_to, 0).text()

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
    def __init__(self, dataset, parent=None):
        super(AttributeTable, self).__init__(parent)

        self.data = dataset

        self.setRowCount(dataset.attribute_count)
        self.setColumnCount(2)

        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Attribute Order'))
        self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Highlight'))

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)

        counter = 0
        for ele in dataset.attribute_names:
            item = QtWidgets.QTableWidgetItem(str(ele))
            self.setItem(counter, 0, item)

            if self.data.plot_type == 'SPC' or self.data.plot_type == 'DSC2':
                if counter % 2 == 0:
                    checkbox = CheckBox(counter, self.data, 'class', parent=self)
                    self.setCellWidget(counter, 1, checkbox)
            else:
                checkbox = CheckBox(counter, self.data, 'class', parent=self)
                self.setCellWidget(counter, 1, checkbox)

            counter += 1

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
