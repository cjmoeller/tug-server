from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import time
import struct
import math


class Plot(QtGui.QMainWindow):


    def __init__(self, queueList, plottingQueues, parent=None):
        super(Plot, self).__init__(parent)

        #### Useable Vars
        self.accX, self.accY, self.accZ = queueList[0:3]
        self.rotX, self.rotY, self.rotZ = queueList[3:6]
        self.accXY, self.rotXY, self.steps, self.integRotZ = queueList[6:10]
        self.accTime, self.rotTime, self.stepsTime = queueList[10:13]


        #### PlottingQueues
        self.fftQueue, self.ifftQueue = plottingQueues[0:2]

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
        self.otherplot3 = self.canvas.addPlot(title="Acc Z-Axis")
        self.h3 = self.otherplot3.plot(pen='y')

        self.canvas.nextRow()

        self.otherplot4 = self.canvas.addPlot(title="Magnitude Rot XY-Plane")
        self.h4 = self.otherplot4.plot(pen='y')
        self.otherplot5 = self.canvas.addPlot(title="Integrated Rot Z-Axis")
        self.h5 = self.otherplot5.plot(pen='y')

        self.canvas.nextRow()

        self.otherplot6 = self.canvas.addPlot(title="Steps")
        self.h6 = self.otherplot6.plot(pen='y')

        self.otherplot7 = self.canvas.addPlot(title="FFT")
        self.h7 = self.otherplot7.plot(pen='y')


        ### Set Ranges #####################

        self.otherplot.setYRange(-20, 20, padding=0)
        self.otherplot3.setYRange(-20, 20, padding=0)
        self.otherplot4.setYRange(-20, 20, padding=0)


        self.otherplot7.setYRange(-5,110)



        #### Set Data  #####################

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        #### Start  #####################
        self._update()

    def _update(self):

        self.h1.setData(self.accXY)
        self.h3.setData(self.accZ)

        self.h4.setData(self.rotXY)
        self.h5.setData(self.integRotZ)
        self.h6.setData(self.steps)
        # self.h7.setData(self.fftQueue)

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