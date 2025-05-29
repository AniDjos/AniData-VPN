# Module de compatibilité pour faciliter la transition PyQt5 -> PySide6
from PySide6 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

# Alias pour les noms de classe PyQt5
QtCore.pyqtSignal = QtCore.Signal
QtCore.pyqtSlot = QtCore.Slot
QtCore.pyqtProperty = QtCore.Property
