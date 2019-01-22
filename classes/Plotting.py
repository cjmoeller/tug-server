from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import time
import settings

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
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)
        self.mainbox.layout().addWidget(self.canvas)

        self.predictionLabel = QtGui.QLabel()
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

        self.otherplot7 = self.canvas.addPlot(title="FFT", labels={'left':"Mag", 'bottom': "Hz"})
        self.h7 = self.otherplot7.plot(pen='y')


        ### Set Ranges #####################

        # self.otherplot.setYRange(-20, 20, padding=0)
        self.otherplot5.setYRange(-200, 350, padding=0)
        self.otherplot4.setYRange(-200, 350, padding=0)

        self.otherplot7.setYRange(-5,110)



        #### Set Data  #####################

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        #### Start  #####################
        self._update()

    def _update(self):

        if self.accXY:
            accXYtime, accXY = map(list, zip(*self.accXY))
            self.h1.setData(accXYtime, accXY)

            accZtime, accZ = map(list, zip(*self.accZ))
            self.h3.setData(accZtime, accZ)

        if self.rotXY:
            rotXYTime, rotXY = map(list, zip(*self.rotXY))
            self.h4.setData(self.integRotXY)

            rotZTime, rotZ= map(list, zip(*self.accXY))
            self.h5.setData(self.integRotZ)

        if self.steps:
            stepsTime, steps = map(list, zip(*self.steps))
            self.h6.setData(stepsTime, steps)

        if self.fftQueue:
            freqs, mag = map(list, zip(*self.fftQueue))
            self.h7.clear()
            self.h7.setData(freqs, mag)


        if settings.LASTPREDICTION == 0:
            self.predictionLabel.setText("laufen oder sitzen")
        elif settings.LASTPREDICTION == 1:
            self.predictionLabel.setText("Aufstehen")
        elif settings.LASTPREDICTION == 2:
            self.predictionLabel.setText("Umdrehen")
        elif settings.LASTPREDICTION == 3:
            self.predictionLabel.setText("Hinsetzen")



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