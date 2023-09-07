from PyQt6.QtWidgets import QMessageBox

class getWarning:
    def noDataWarning(self):
        no_data_message = QMessageBox()
        no_data_message.setWindowTitle('Warning: No dataset')
        no_data_message.setText('Please upload dataset before generating plot.')
        no_data_message.setIcon(QMessageBox.Icon.Warning)
        no_data_message.setStandardButtons(QMessageBox.StandardButtons.Ok)

        no_data_message.exec()

    def oddFeatureCount(self):
        no_data_message = QMessageBox()
        no_data_message.setWindowTitle('Warning: Odd Feature Count')
        no_data_message.setText('This plot requires an even feature count.')
        no_data_message.setIcon(QMessageBox.Icon.Warning)
        no_data_message.setStandardButtons(QMessageBox.StandardButtons.Ok)

        # Uncomment this line to execute the message box
        # no_data_message.exec()
