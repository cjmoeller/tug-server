import settings
import threading
from collections import deque

import numpy as np
# from numpy.fft import rfft, fftshift, irfft, ifftshift, fft, ifft
import time
from scipy.fftpack import fft, ifft, fftshift, rfft, rfftfreq


class ML(threading.Thread):

    def __init__(self, queueList, plottingQueues):
        threading.Thread.__init__(self)

        self.FRAMESIZE = settings.FRAMESIZE

        #### Useable Vars
        self.accX, self.accY, self.accZ = queueList[0:3]
        self.rotX, self.rotY, self.rotZ = queueList[3:6]
        self.accXY, self.rotXY, self.steps, self.integRotZ = queueList[6:10]
        self.accTime, self.rotTime, self.stepsTime = queueList[10:13]
        self.integRotXY = queueList[13]

        #### PlottingQueues
        self.fftQueue, self.ifftQueue = plottingQueues[0:2]


        self.accXYdeq = deque(maxlen=self.FRAMESIZE)
        self.accZdeq = deque(maxlen=self.FRAMESIZE)
        self.rotXYIntegdeq = deque(maxlen=self.FRAMESIZE)
        self.rotZIntegdeq = deque(maxlen=self.FRAMESIZE)


        self.model = settings.create_model()
        self.model.load_weights(settings.MODEL)



    def run(self):
        while True:
            newVal = False
            if not self.accXY.empty():
                accXYVal = self.accXY.get()
                self.accXYdeq.append(accXYVal[1])
                newVal = True
            if not self.accZ.empty():
                accZVal = self.accZ.get()
                self.accZdeq.append(accZVal[1])
                newVal = True
            if not self.integRotXY.empty():
                rotXYIntegVal = self.integRotXY.get()
                self.rotXYIntegdeq.append(rotXYIntegVal)
                newVal = True
            if not self.integRotZ.empty():
                rotZIntegVal = self.integRotZ.get()
                self.rotZIntegdeq.append(rotZIntegVal)
                newVal = True

            if newVal and len(self.accXYdeq) >= settings.FRAMESIZE and len(self.rotXYIntegdeq) >= settings.FRAMESIZE:

                actualFrame = np.array([list(self.accXYdeq), list(self.rotXYIntegdeq), list(self.accZdeq), list(self.rotZIntegdeq)])
                actualFrame = np.swapaxes(actualFrame, 0, 1)
                absolute = np.absolute(actualFrame)
                amax = np.amax(absolute, axis=0)
                maxabs = abs(amax)
                actualFrame /= maxabs

                actualFrame = np.reshape(actualFrame, (1, settings.FRAMESIZE, settings.NUM_SENSORS))

                prediction = self.model.predict_classes(actualFrame)
                print(prediction)
                settings.LASTPREDICTION = prediction[0][-1]






        # print("Lol")
        #
        # for body in iter(self.accXY.get, None):
        #     self.workingQueue.append(body)
        #     counter += 1
        #     if counter == self.FRAMESIZE/10:
        #         timestep = (self.workingQueue[-1][0] - self.workingQueue[0][0]) / float(len(self.workingQueue))
        #         self.FFT(self.workingQueue, timestep)
        #         counter = 0



    # def FFT(self, values: deque, timestep):
    #     fourier = rfft([y for (x,y) in self.workingQueue])
    #     fourier = np.abs(fourier)
    #     N = len(values)
    #     samplerate = 1/timestep
    #     # freqs = np.fft.fftfreq(N)*samplerate
    #     freqs = rfftfreq(len(fourier), 1/timestep)
    #
    #     self.fftQueue.clear()
    #     for time, value in zip(freqs, fourier):
    #         self.fftQueue.append((time, value))

