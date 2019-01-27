import settings
import threading
from collections import deque, Counter
import tensorflow as tf
from joblib import load

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

        self.predictedData = []
        self.numPredictions = 0
        self.testRunning = False
        self.doneActivities = []
        self.startingTime = 0

        # self.model = settings.create_model()
        # self.model.load_weights(settings.MODEL)
        # self.model._make_predict_function()

        self.tree = load('tree.joblib')

    def analyze(self, prediction):
        for i in range(0, len(prediction[0])):
            for j in range(0, 8):
                while len(self.predictedData) <= self.numPredictions + i * 8 + j:
                    self.predictedData.append([])
                self.predictedData[self.numPredictions + i * 8 + j].append(prediction[0][i])

    def stop_test(self):
        endingTime = int(round(time.time() * 1000))
        print('test finished!')
        test_results = []
        print(self.predictedData)
        for i in range(0, len(self.predictedData)):
            votes = self.predictedData[i]
            result = np.argmax(np.bincount(votes))
            test_results.append(result)
        print(test_results)
        time_period = ((endingTime - self.startingTime) / 1000) / len(test_results)
        last_state = test_results[0]
        current_count = 0
        print("========== TEST SUMMARY ===========")
        predicted_time = 0
        test_running = False
        for i in range(1, len(test_results)):
            if test_results[i] == last_state:
                current_count += 1
            else:
                print("Activity " + str(last_state) + " for " + str(current_count * time_period) + "s")
                if test_running:
                    predicted_time += current_count * time_period
                if last_state == 3:  # ende
                    test_running = False
                if last_state == 4:  # sitzen nicht mehr mit reinrechnen
                    test_running = True
                last_state = test_results[i]
                current_count = 0
        print("Predicted time: " + str(predicted_time) + "s")
        self.predictedData[:] = []
        self.numPredictions = 0
        self.testRunning = False

    def run(self):
        acc = False
        rot = False
        while True:
            if not self.accXY.empty():
                accXYVal = self.accXY.get()
                self.accXYdeq.append(accXYVal[1])
                acc = True
            if not self.accZ.empty():
                accZVal = self.accZ.get()
                self.accZdeq.append(accZVal[1])
                newVal = True
                acc = True
            if not self.integRotXY.empty():
                rotXYIntegVal = self.integRotXY.get()
                self.rotXYIntegdeq.append(rotXYIntegVal)
                rot = True
            if not self.integRotZ.empty():
                rotZIntegVal = self.integRotZ.get()
                self.rotZIntegdeq.append(rotZIntegVal)
                rot = True

            if acc and rot and len(self.accXYdeq) >= settings.FRAMESIZE and len(
                    self.rotXYIntegdeq) >= settings.FRAMESIZE:

                actualFrame = np.array(
                    [list(self.accXYdeq), list(self.rotXYIntegdeq), list(self.accZdeq), list(self.rotZIntegdeq)])
                actualFrame = np.swapaxes(actualFrame, 0, 1)
                maxabs = abs(np.amax(np.absolute(actualFrame), axis=0))
                actualFrame /= settings.DIVISIOR

                # actualFrame = np.reshape(actualFrame, (1, settings.FRAMESIZE, settings.NUM_SENSORS))

                actualFrame = np.reshape(actualFrame, (1, 320))
                # prediction = self.model.predict_classes(actualFrame)

                prediction = self.tree.predict(actualFrame)

                # print(prediction)
                prediction = prediction.astype(int)

                counts = np.bincount(prediction[0])
                last = -1
                if len(settings.LASTPREDICTION) > 0:
                    data = Counter(settings.LASTPREDICTION)
                    last = (max(settings.LASTPREDICTION, key=data.get))

                if self.testRunning:
                    self.analyze(prediction)
                    self.numPredictions += 1
                    if np.argmax(counts) not in self.doneActivities:
                        self.doneActivities.append(np.argmax(counts))
                    if np.argmax(counts) == 4 and len(self.doneActivities) > 3:
                        self.stop_test()
                        self.doneActivities = []
                elif last == 4 and np.argmax(counts) == 1:
                    self.testRunning = True
                    self.startingTime = int(round(time.time() * 1000))
                    print('Test started!')

                settings.LASTPREDICTION.append(prediction[0][-2])
                rot = False
                acc = False

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
