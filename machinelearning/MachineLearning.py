import threading
from collections import deque
import numpy as np
# from numpy.fft import rfft, fftshift, irfft, ifftshift, fft, ifft
import time
from scipy.fftpack import fft, ifft, fftshift, rfft, rfftfreq

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


    def run(self):
        counter = 0

        print("Lol")

        for body in iter(self.accXY.get, None):
            self.workingQueue.append(body)
            counter += 1
            if counter == self.FRAMESIZE/10:
                timestep = (self.workingQueue[-1][0] - self.workingQueue[0][0]) / float(len(self.workingQueue))
                self.FFT(self.workingQueue, timestep)
                counter = 0



    def FFT(self, values: deque, timestep):
        fourier = rfft([y for (x,y) in self.workingQueue])
        fourier = np.abs(fourier)
        N = len(values)
        samplerate = 1/timestep
        # freqs = np.fft.fftfreq(N)*samplerate
        freqs = rfftfreq(len(fourier), 1/timestep)

        self.fftQueue.clear()
        for time, value in zip(freqs, fourier):
            self.fftQueue.append((time, value))

