
import sys
from RMQ import RMQConnection
from queue import Queue
from pyqtgraph.Qt import QtCore, QtGui
from Plotting import Plot


# Create a global channel variable to hold our channel object in
channel = None

xs = []
ys = []
y2s = []


    # def handle_delivery(channel, method, header, body):
    #     """Called when we receive a message from RabbitMQ"""
    #
    #     global xs
    #     global ys
    #     global y2s
    #
    #     measurement_type = body[0]
    #     time = struct.unpack('>q', body[1:9])
    #
    #     v1 = struct.unpack('>f', body[9:13])[0]
    #     v2 = struct.unpack('>f', body[13:17])[0]
    #     v3 = struct.unpack('>f', body[17:21])[0]
    #
    #     print("TYPE: " + str(measurement_type) + " | " + str(time) + " Measurement(" + str(v1) + " | " + str(
    #         v2) + " | " + str(v3) + ")")
    #     xs.append(str(time))
    #     xs = xs[-100:]
    #     ys.append(float(v1))
    #     ys = ys[-100:]
    #     y2s.append(float(v2))
    #     y2s = y2s[-100:]
#





if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    messageQueue = Queue()

    thisplot = Plot(messageQueue)
    thisplot.show()

    td = RMQConnection(messageQueue)
    td.start()


    sys.exit(app.exec_())
