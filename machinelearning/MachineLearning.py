import threading
from collections import deque
import numpy as np
import time

class ML(threading.Thread):

    def __init__(self, queueList, plottingQueues, FRAMESIZE):
        threading.Thread.__init__(self)

        self.FRAMESIZE = FRAMESIZE
        #### Useable Vars
        self.accX, self.accY, self.accZ = queueList[0:3]
        self.rotX, self.rotY, self.rotZ = queueList[3:6]
        self.accXY, self.rotXY, self.steps, self.integRotZ = queueList[6:10]
        self.accTime, self.rotTime, self.stepsTime = queueList[10:13]

        #### PlottingQueues
        self.fftQueue, self.ifftQueue = plottingQueues[0:2]


        self.workingQueue = deque(maxlen=FRAMESIZE)
        self.workingTime = deque(maxlen=FRAMESIZE)
        counter = 0

        print("Lol")

        # for body in iter(self.accXY.get, None):
        #     self.workingQueue.append(body)
        #     counter += 1
        #     if counter == FRAMESIZE/2:
        #         timestep = (self.accTime[-1] - self.accTime[0]) / float(len(self.accTime))
        #         self.FFT(self.workingQueue, timestep)
        #         counter = 0

    def FFT(self, values: deque, timestep):
        fourier = np.fft.fft(values)
        N = len(values)
        samplerate = 1/timestep
        freqs = np.fft.fftfreq(N)*samplerate

        # self.fftQueue.clear()
        for time, value in zip(freqs, fourier):
            self.fftQueue.append(value)

