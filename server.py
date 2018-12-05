
import sys
from RMQ import RMQConnection
from queue import Queue
from pyqtgraph.Qt import QtCore, QtGui
from Plotting import Plot
from collections import deque
from DataHandler import DataHandler



if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    FRAMESIZE = 500

    messageQueue = Queue()

    queueList = []

    accX = deque(maxlen=FRAMESIZE)
    accY = deque(maxlen=FRAMESIZE)
    accZ = deque(maxlen=FRAMESIZE)

    rotX = deque(maxlen=FRAMESIZE)
    rotY = deque(maxlen=FRAMESIZE)
    rotZ = deque(maxlen=FRAMESIZE)

    accXY = deque(maxlen=FRAMESIZE)
    rotXY = deque(maxlen=FRAMESIZE)
    steps = deque(maxlen=FRAMESIZE)

    integRotZ = deque(maxlen=FRAMESIZE)



    queueList.append(accX)
    queueList.append(accY)
    queueList.append(accZ)

    queueList.append(rotX)
    queueList.append(rotY)
    queueList.append(rotZ)

    queueList.append(accXY)
    queueList.append(rotXY)
    queueList.append(steps)

    queueList.append(integRotZ)

    dataHandler = DataHandler(messageQueue, queueList)
    dataHandler.start()

    thisplot = Plot(queueList)
    thisplot.show()

    td = RMQConnection(messageQueue)
    td.start()

    sys.exit(app.exec_())
