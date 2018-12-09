
import sys
from RMQ import RMQConnection
from queue import Queue
from pyqtgraph.Qt import QtCore, QtGui
from Plotting import Plot
from collections import deque
from DataHandler import DataHandler
from machinelearning.MachineLearning import ML

def createDequeList():
    queueList = []

    accX = deque(maxlen=FRAMESIZE)
    accY = deque(maxlen=FRAMESIZE)
    accZ = deque(maxlen=FRAMESIZE)
    accTime = deque(maxlen=FRAMESIZE)

    rotX = deque(maxlen=FRAMESIZE)
    rotY = deque(maxlen=FRAMESIZE)
    rotZ = deque(maxlen=FRAMESIZE)
    rotTime=deque(maxlen=FRAMESIZE)

    accXY = deque(maxlen=FRAMESIZE)
    rotXY = deque(maxlen=FRAMESIZE)
    integRotZ = deque(maxlen=FRAMESIZE)

    steps = deque(maxlen=FRAMESIZE)
    stepsTime = deque(maxlen=FRAMESIZE)

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
    queueList.append(accTime)
    queueList.append(rotTime)
    queueList.append(stepsTime)

    return queueList


def createQueueList():
    queueList = []

    accX = Queue()
    accY = Queue()
    accZ = Queue()
    accTime = Queue()

    rotX = Queue()
    rotY = Queue()
    rotZ = Queue()
    rotTime=Queue()

    accXY = Queue()
    rotXY = Queue()
    integRotZ = Queue()

    steps = Queue()
    stepsTime = Queue()

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
    queueList.append(accTime)
    queueList.append(rotTime)
    queueList.append(stepsTime)

    return queueList


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    FRAMESIZE = 500


    plottingDataQueue = createDequeList()
    machineLearningDataQueue = createQueueList()

    rmqQueue = Queue()

    machineLearningPlottingQueues = []

    fftQueue = deque(maxlen=FRAMESIZE)
    ifftQueue = deque(maxlen=FRAMESIZE)

    machineLearningPlottingQueues.append(fftQueue)
    machineLearningPlottingQueues.append(ifftQueue)


    thisplot = Plot(plottingDataQueue, machineLearningPlottingQueues)
    thisplot.show()

    dataHandler = DataHandler(rmqQueue, plottingDataQueue, machineLearningDataQueue)
    dataHandler.start()


    machineLearning = ML(machineLearningDataQueue, machineLearningPlottingQueues, FRAMESIZE)
    machineLearning.start()

    td = RMQConnection(rmqQueue)
    td.start()




    sys.exit(app.exec_())
