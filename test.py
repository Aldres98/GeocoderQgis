#!/usr/bin/python3
# Threading example with QThread and moveToThread (PyQt5)
import sys
import time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThreadPool, QThread

from geocoder_worker import GeocoderWorker



class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.obj = GeocoderWorker("a", "b", "c")  # no parent!
        self.thread = QThread()  # no parent!

        # 2 - Connect Worker`s Signals to Form method slots to post data.
        self.obj.intReady.connect(self.onIntReady)

        # 3 - Move the Worker object to the Thread object
        self.obj.moveToThread(self.thread)

        # 4 - Connect Worker Signals to the Thread slots
        self.obj.finished.connect(self.thread.quit)

        # 5 - Connect Thread started signal to Worker operational slot method
        self.thread.started.connect(self.obj.run)

        # * - Thread finished signal will close the app if you want!
        # self.thread.finished.connect(app.exit)

        # 6 - Start the thread
        self.thread.start()

    def signalExample(self, number):
        print(number)

    def onIntReady(self, num):
        print(num)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    gui = Main()
    sys.exit(app.exec_())