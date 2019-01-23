from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import *
import pyqtgraph as pg
import time
import settings
from collections import Counter

class Plot(QtGui.QMainWindow):

    lastState = 0
    def pushBtn(self):
        if(settings.keyboardLabel != 0):
            self.lastState = settings.keyboardLabel
            settings.keyboardLabel = 0
        else:
            self.lastState = (self.lastState + 1) % 4
            settings.keyboardLabel = self.lastState

        self.btn.setText("Label: " + str(settings.keyboardLabel))


    def __init__(self, queueList, plottingQueues, parent=None):
        super(Plot, self).__init__(parent)


        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        #### Useable Vars
        self.accX, self.accY, self.accZ = queueList[0:3]
        self.rotX, self.rotY, self.rotZ = queueList[3:6]
        self.accXY, self.rotXY, self.steps, self.integRotZ = queueList[6:10]
        self.accTime, self.rotTime, self.stepsTime = queueList[10:13]
        self.integRotXY = queueList[13]


        #### PlottingQueues
        self.fftQueue, self.ifftQueue = plottingQueues[0:2]

        #### Create Gui Elements ###########
        self.resize(1200, 900)

        self.mainbox = QtGui.QWidget()
        self.mainbox.setAutoFillBackground(True)
        # palette = self.mainbox.palette()
        # palette.setColor(self.mainbox.backgroundRole(), pg.mkColor('w'))
        # self.mainbox.setPalette(palette)


        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)
        self.mainbox.layout().addWidget(self.canvas)

        self.predictionLabel = QtGui.QLabel()
        self.predictionLabel.setAlignment(Qt.AlignCenter)
        font = QtGui.QFont("Times", 20, QtGui.QFont.Bold)
        self.predictionLabel.setFont(font)
        self.mainbox.layout().addWidget(self.predictionLabel)

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)

        self.btn = QtGui.QPushButton('Label: 0')
        self.btn.clicked.connect(lambda:self.pushBtn())
        self.mainbox.layout().addWidget(self.btn)

        #  line plot
        self.otherplot = self.canvas.addPlot(title="Magnitude Acc XY-Plane")
        self.h1 = self.otherplot.plot(pen='b')
        self.otherplot3 = self.canvas.addPlot(title="Acc Z-Axis")
        self.h3 = self.otherplot3.plot(pen='b')

        self.canvas.nextRow()

        self.otherplot4 = self.canvas.addPlot(title="Integrated Magnitude Rot XY-Plane")
        self.h4 = self.otherplot4.plot(pen='b')
        self.otherplot5 = self.canvas.addPlot(title="Integrated Rot Z-Axis")
        self.h5 = self.otherplot5.plot(pen='b')

        self.canvas.nextRow()

        self.otherplot6 = self.canvas.addPlot(title="Raw Acc")
        self.otherplot6.addLegend()
        self.h6x = self.otherplot6.plot(pen='b', name='X')
        self.h6y = self.otherplot6.plot(pen='g', name='Y')
        self.h6z = self.otherplot6.plot(pen='r', name='Z')

        self.otherplot7 = self.canvas.addPlot(title="Raw Rot")
        self.otherplot7.addLegend()
        self.h7x = self.otherplot7.plot(pen='b', name='X')
        self.h7y = self.otherplot7.plot(pen='g', name='Y')
        self.h7z = self.otherplot7.plot(pen='r', name='Z')


        ### Set Ranges #####################

        # self.otherplot.setYRange(-20, 20, padding=0)
        self.otherplot5.setYRange(-200, 350, padding=0)
        self.otherplot4.setYRange(-200, 350, padding=0)
        # self.otherplot7.setYRange(-5,110)

        color = (0,119,239,120)


        lr = pg.LinearRegionItem(values = [settings.PLOTTINGFRAMESIZE-settings.FRAMESIZE, settings.PLOTTINGFRAMESIZE])
        lr.setBrush(color)
        self.otherplot.addItem(lr)
        lr = pg.LinearRegionItem([settings.PLOTTINGFRAMESIZE - settings.FRAMESIZE, settings.PLOTTINGFRAMESIZE])
        lr.setBrush(color)
        self.otherplot3.addItem(lr)
        lr = pg.LinearRegionItem([settings.PLOTTINGFRAMESIZE - settings.FRAMESIZE, settings.PLOTTINGFRAMESIZE])
        lr.setBrush(color)
        self.otherplot4.addItem(lr)
        lr = pg.LinearRegionItem([settings.PLOTTINGFRAMESIZE - settings.FRAMESIZE, settings.PLOTTINGFRAMESIZE])
        lr.setBrush(color)
        self.otherplot5.addItem(lr)



        #### Set Data  #####################

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        #### Start  #####################
        self._update()

    def _update(self):

        if self.accXY:
            accXYtime, accXY = map(list, zip(*self.accXY))
            self.h1.setData(accXY)

            accZtime, accZ = map(list, zip(*self.accZ))
            self.h3.setData(accZ)

        if self.rotXY:
            rotXYTime, rotXY = map(list, zip(*self.rotXY))
            self.h4.setData(self.integRotXY)

            rotZTime, rotZ= map(list, zip(*self.accXY))
            self.h5.setData(self.integRotZ)

        if self.accX:
            accXTime, accXVal = map(list, zip(*self.accX))
            accYTime, accYVal = map(list, zip(*self.accY))
            accZTime, accZVal = map(list, zip(*self.accZ))
            self.h6x.setData(accXVal)
            self.h6y.setData(accYVal)
            self.h6z.setData(accZVal)

        if self.rotX:
            rotXTime, rotXVal = map(list, zip(*self.rotX))
            rotYTime, rotYVal = map(list, zip(*self.rotY))
            rotZTime, rotZVal = map(list, zip(*self.rotZ))
            self.h7x.setData(rotXVal)
            self.h7y.setData(rotYVal)
            self.h7z.setData(rotZVal)

        if len(settings.LASTPREDICTION) > 0:
            data = Counter(settings.LASTPREDICTION)
            prediction = (max(settings.LASTPREDICTION, key=data.get))


            if prediction == 0:
                self.predictionLabel.setText("Laufen")
            elif prediction == 1:
                self.predictionLabel.setText("Aufstehen")
            elif prediction == 2:
                self.predictionLabel.setText("Umdrehen")
            elif prediction == 3:
                self.predictionLabel.setText("Hinsetzen")
            elif prediction == 4:
                self.predictionLabel.setText("Sitzen")



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