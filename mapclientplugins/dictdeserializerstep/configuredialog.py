import os
from PySide2 import QtWidgets
from mapclientplugins.dictdeserializerstep.ui_configuredialog import Ui_ConfigureDialog

INVALID_STYLE_SHEET = 'background-color: rgba(239, 0, 0, 50)'
DEFAULT_STYLE_SHEET = ''


class ConfigureDialog(QtWidgets.QDialog):
    """
    Configure dialog to present the user with the options to configure this step.
    """

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self._ui = Ui_ConfigureDialog()
        self._ui.setupUi(self)

        # Keep track of the previous identifier so that we can track changes
        # and know how many occurrences of the current identifier there should
        # be.
        self._previousIdentifier = ''
        # Set a place holder for a callable that will get set from the step.
        # We will use this method to decide whether the identifier is unique.
        self.identifierOccursCount = None
        self._previousLocation = ''

        self._makeConnections()

    def _makeConnections(self):
        self._ui.identifier_lineEdit.textChanged.connect(self.validate)
        self._ui.input_lineEdit.textChanged.connect(self.validate)
        self._ui.inputLocation_pushButton.clicked.connect(self._input_location_push_button_clicked)

    def _input_location_push_button_clicked(self):
        location, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption='Choose Input File',
                                                            dir=self._previousLocation)
        if location:
            self._previousLocation = os.path.dirname(location)
            self._ui.input_lineEdit.setText(location)

    def accept(self):
        """
        Override the accept method so that we can confirm saving an
        invalid configuration.
        """
        result = QtWidgets.QMessageBox.Yes
        if not self.validate():
            result = QtWidgets.QMessageBox.warning(self, 'Invalid Configuration',
                                                   'This configuration is invalid.  Unpredictable behaviour may result if you choose \'Yes\', are you sure you want to save this configuration?)',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                   QtWidgets.QMessageBox.No)

        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QDialog.accept(self)

    def validate(self):
        """
        Validate the configuration dialog fields.  For any field that is not valid
        set the style sheet to the INVALID_STYLE_SHEET.  Return the outcome of the
        overall validity of the configuration.
        """
        # Determine if the current identifier is unique throughout the workflow
        # The identifierOccursCount method is part of the interface to the workflow framework.
        sender = self.sender()
        input_location_valid = False
        input_location = self._ui.input_lineEdit.text()

        if os.path.isfile(input_location):
            input_location_valid = True
            self._ui.input_lineEdit.setStyleSheet(DEFAULT_STYLE_SHEET)
        else:
            self._ui.input_lineEdit.setStyleSheet(INVALID_STYLE_SHEET)

        value = self.identifierOccursCount(self._ui.identifier_lineEdit.text())
        valid = (value == 0) or (value == 1 and self._previousIdentifier == self._ui.identifier_lineEdit.text())
        if valid:
            self._ui.identifier_lineEdit.setStyleSheet(DEFAULT_STYLE_SHEET)
        else:
            self._ui.identifier_lineEdit.setStyleSheet(INVALID_STYLE_SHEET)

        return valid and input_location_valid

    def getConfig(self):
        """
        Get the current value of the configuration from the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        """
        self._previousIdentifier = self._ui.identifier_lineEdit.text()
        config = {'identifier': self._ui.identifier_lineEdit.text(),
                  'input': self._ui.input_lineEdit.text()}
        return config

    def setConfig(self, config):
        """
        Set the current value of the configuration for the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        """
        self._previousIdentifier = config['identifier']
        self._ui.identifier_lineEdit.setText(config['identifier'])
        self._ui.input_lineEdit.setText(config['input'])
