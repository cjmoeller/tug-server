from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import time
import struct
import math


class Plot(QtGui.QMainWindow):

    FRAMESIZE = 500

    def __init__(self, queue, parent=None):
        super(Plot, self).__init__(parent)

        self.queue = queue

        #### Create Gui Elements ###########
        self.resize(1200, 900)

        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)



        #  line plot
        self.otherplot = self.canvas.addPlot(title="Magnitude Acc XY-Plane")
        self.h1 = self.otherplot.plot(pen='y')
        # self.otherplot2 = self.canvas.addPlot()
        # self.h2 = self.otherplot2.plot(pen='y')
        self.otherplot3 = self.canvas.addPlot(title="Acc Z-Axis")
        self.h3 = self.otherplot3.plot(pen='y')

        self.canvas.nextRow()

        self.otherplot4 = self.canvas.addPlot(title="Magnitude Rot XY-Plane")
        self.h4 = self.otherplot4.plot(pen='y')
        self.otherplot5 = self.canvas.addPlot(title="Integrated Rot Z-Axis")
        self.h5 = self.otherplot5.plot(pen='y')
        # self.otherplot6 = self.canvas.addPlot()
        # self.h6 = self.otherplot6.plot(pen='y')

        ### Set Ranges #####################

        self.otherplot.setYRange(-20, 20, padding=0)
        # self.otherplot2.setYRange(-20, 20, padding=0)
        self.otherplot3.setYRange(-20, 20, padding=0)
        self.otherplot4.setYRange(-20, 20, padding=0)
        # self.otherplot5.setYRange(-20, 20, padding=0)
        # self.otherplot6.setYRange(-20, 20, padding=0)


        #### Set Data  #####################

        self.y1 = []
        # self.y2 = []
        self.y3 = []

        self.y4 = []
        self.y5 = []
        self.y6 = []

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        #### Start  #####################
        self._update()

    def _update(self):

        while not self.queue.empty():
            body = self.queue.get()
            measurement_type = body[0]
            if measurement_type == 3:
                # time = struct.unpack('>q', body[1:9])[0]

                v1 = struct.unpack('>f', body[9:13])[0]
                v2 = struct.unpack('>f', body[13:17])[0]
                v3 = struct.unpack('>f', body[17:21])[0]

                self.y1.append(math.sqrt(float(v1)*float(v1) + float(v2)*float(v2)))
                # self.y2.append(float(v2))
                self.y3.append(float(v3))

            if measurement_type == 4:
                # time = struct.unpack('>q', body[1:9])[0]

                v4 = struct.unpack('>f', body[9:13])[0]
                v5 = struct.unpack('>f', body[13:17])[0]
                v6 = struct.unpack('>f', body[17:21])[0]

                self.y4.append(math.sqrt(float(v4)*float(v4) + float(v5)*float(v5)))
                self.y6.append(float(v6))
                self.y5.append(np.trapz(self.y6[-100:]))


        self.y1 = self.y1[-self.FRAMESIZE:]
        # self.y2 = self.y2[-self.FRAMESIZE:]
        self.y3 = self.y3[-self.FRAMESIZE:]

        self.y4 = self.y4[-self.FRAMESIZE:]
        self.y5 = self.y5[-self.FRAMESIZE:]
        self.y6 = self.y6[-self.FRAMESIZE:]

        self.h1.setData(self.y1)
        # self.h2.setData(self.y2)
        self.h3.setData(self.y3)

        self.h4.setData(self.y4)
        self.h5.setData(self.y5)
        # self.h6.setData(self.y6)


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