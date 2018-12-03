from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import time
import struct


class Plot(QtGui.QMainWindow):
    def __init__(self, queue, parent=None):
        super(Plot, self).__init__(parent)

        self.queue = queue

        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)



        # self.canvas.nextRow()
        #  line plot
        self.otherplot = self.canvas.addPlot()
        self.h2 = self.otherplot.plot(pen='y')
        self.otherplot2 = self.canvas.addPlot()
        self.h3 = self.otherplot2.plot(pen='y')


        #### Set Data  #####################

        self.y1 = []
        self.y2 = []


        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        #### Start  #####################
        self._update()

    def _update(self):

        while not self.queue.empty():
            body = self.queue.get()
            measurement_type = body[0]
            if measurement_type == 0:
                # time = struct.unpack('>q', body[1:9])[0]

                v1 = struct.unpack('>f', body[9:13])[0]
                v2 = struct.unpack('>f', body[13:17])[0]
                v3 = struct.unpack('>f', body[17:21])[0]

                self.y1.append(float(v2))
                self.y2.append(float(v3))

        self.y1 = self.y1[-5000:]
        self.y2 = self.y2[-5000:]
        self.h2.setData(self.y1)
        self.h3.setData(self.y2)

        now = time.time()
        dt = (now-self.lastupdate)
        if dt <= 0:
            dt = 0.000000000001
        fps2 = 1.0 / dt
        self.lastupdate = now
        self.fps = self.fps * 0.9 + fps2 * 0.1
        tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
        self.label.setText(tx)
        QtCore.QTimer.singleShot(0, self._update)
        self.counter += 1