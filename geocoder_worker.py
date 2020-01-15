# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
from .geocode import *
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import *
import traceback


class GeocoderWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)


    def __init__(self, addresses, key, layer):
        super().__init__()
        self.addresses = addresses
        self.max_progress_value = len(addresses)
        self.key = key
        self.layer = layer
        self.killed = False

    @pyqtSlot()
    def run(self):
        count = 0
        addresses = here(self.key, self.addresses)
        for address in addresses:
            if(self.progress == self.max_progress_value):
                self.finished.emit()
            count += 1
            self.progress.emit(count)
            prov = self.layer.dataProvider()
            prov.addAttributes([QgsField("Address", QVariant.String)])
            self.layer.updateFields()
            point = QgsPointXY(address['Longitude'], address['Latitude'])
            feat = QgsFeature()
            # feat.setAttributes(address["AddressLabel"])
            feat.setAttributes([address["AddressLabel"]])
            feat.setGeometry(QgsGeometry.fromPointXY(point))
            prov.addFeatures([feat])
            self.layer.updateExtents()
        self.finished.emit()

