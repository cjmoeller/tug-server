
import sys
from RMQ import RMQConnection
from queue import Queue
from pyqtgraph.Qt import QtCore, QtGui
from Plotting import Plot


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    messageQueue = Queue()

    thisplot = Plot(messageQueue)
    thisplot.show()

    td = RMQConnection(messageQueue)
    td.start()


    sys.exit(app.exec_())
