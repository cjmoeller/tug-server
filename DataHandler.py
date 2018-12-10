import time
import threading
import struct
import math
import numpy as np
from collections import deque

class DataHandler(threading.Thread):

    SMALLERFRAME = 100

    def __init__(self, queue, plottingDataQueue, machineLearningDataQeue, args, text_file):
        threading.Thread.__init__(self)
        self.queue = queue
        self.plottingDataQueue = plottingDataQueue
        self.machineLearningDataQueue = machineLearningDataQeue
        self.args = args
        self.text_file = text_file

        # #### Useable Vars
        # self.accPlotX, self.accPlotY, self.accPlotZ = plottingDataQueue[0:3]
        # self.rotPlotX, self.rotPlotY, self.rotPlotZ = plottingDataQueue[3:6]
        # self.accPlotXY, self.rotPlotXY, self.stepsPlot, self.integRotPlotZ = plottingDataQueue[6:10]
        # self.accPlotTime, self.rotPlotTime, self.stepsPlotTime = plottingDataQueue[10:13]
        #
        # #### Useable Vars
        # self.accMLX, self.accMLY, self.accMLZ = machineLearningDataQeue[0:3]
        # self.rotMLX, self.rotMLY, self.rotMLZ = machineLearningDataQeue[3:6]
        # self.accMLXY, self.rotMLXY, self.stepsML, self.integRotMLZ = machineLearningDataQeue[6:10]
        # self.accTimeML, self.rotTimeML, self.stepsTimeML = machineLearningDataQeue[10:13]

        print("start")


    def run(self):

        #### Temp filler Vars
        self.tempaccX = deque()
        self.tempaccY = deque()
        self.tempaccZ = deque()
        self.tempaccTime = deque()

        self.temprotX = deque()
        self.temprotY = deque()
        self.temprotZ = deque()
        self.temprotTime = deque()

        self.tempSteps = deque()
        self.tempStepsTime = deque()

        self.calcrotZsmall = deque(maxlen=self.SMALLERFRAME)

        for body in iter(self.queue.get, None):
            # print(' [x] received %r' % (body,))
            self.unwrap(body)
            self.tuneValues()
            self.clearTemp()


    def unwrap(self, body):
        measurement_type = body[0]
        if measurement_type == 3:
            time = struct.unpack('>q', body[1:9])[0]

            v1 = struct.unpack('>f', body[9:13])[0]
            v2 = struct.unpack('>f', body[13:17])[0]
            v3 = struct.unpack('>f', body[17:21])[0]

            self.tempaccX.append(v1)
            self.tempaccY.append(v2)
            self.tempaccZ.append(v3)
            self.tempaccTime.append(time)

        if measurement_type == 4:
            time = struct.unpack('>q', body[1:9])[0]

            v1 = struct.unpack('>f', body[9:13])[0]
            v2 = struct.unpack('>f', body[13:17])[0]
            v3 = struct.unpack('>f', body[17:21])[0]

            self.temprotX.append(float(v1))
            self.temprotY.append(float(v2))
            self.temprotZ.append(float(v3))
            self.temprotTime.append(time)

        if measurement_type == 5:
            time = struct.unpack('>q', body[1:9])[0]

            v1 = struct.unpack('>f', body[9:13])[0]
            v2 = 0
            v3 = 0

            self.tempSteps.append(float(v1))
            self.tempStepsTime.append(time)

        if self.args.save:
            self.save_to_file(time, measurement_type, v1, v2, v3)


    def tuneValues(self):
        for rotz in self.temprotZ:
            self.calcrotZsmall.append(rotz)

        self.fillDeque(self.plottingDataQueue)
        self.fillQueue(self.machineLearningDataQueue)


    def fillQueue(self, queue):
        for accx, accy, accz, acctime in zip(self.tempaccX, self.tempaccY, self.tempaccZ, self.tempaccTime):
            queue[0].put((acctime,accx))
            queue[1].put((acctime,accy))
            queue[2].put((acctime,accz))

            queue[6].put((acctime,math.sqrt(accx * accx + accy * accy)))

        # for accz in self.tempaccZ:
        #     queue[2].put(accz)


        # for time in self.tempaccTime:
        #     queue[10].put(time)


        for rotx, roty, rotz, rottime in zip(self.temprotX, self.temprotY, self.temprotZ, self.temprotTime):
            queue[3].put((rottime, rotx))
            queue[4].put((rottime, roty))
            queue[5].put((rottime, rotz))
            queue[7].put((rottime, math.sqrt(rotx * rotx + roty * roty)))

        # for rotz in self.temprotZ:
        #     queue[5].put(rotz)

        # for time in self.temprotTime:
        #     queue[11].put(time)

        # If new Values, calc a new Integral
        tempZ = not len(self.temprotZ) == 0
        if tempZ:
            queue[9].put(np.trapz(self.calcrotZsmall))

        for step,time in zip(self.tempSteps, self.tempStepsTime):
            queue[8].put((time,step))

        # for time in self.tempStepsTime:
        #     queue[12].put(time)

    def fillDeque(self, queue):
        for accx, accy, accz, acctime in zip(self.tempaccX, self.tempaccY, self.tempaccZ, self.tempaccTime):
            queue[0].append((acctime,accx))
            queue[1].append((acctime,accy))
            queue[2].append((acctime,accz))

            queue[6].append((acctime,math.sqrt(accx * accx + accy * accy)))

        # for accz in self.tempaccZ:
        #     queue[2].put(accz)


        # for time in self.tempaccTime:
        #     queue[10].put(time)


        for rotx, roty, rotz, rottime in zip(self.temprotX, self.temprotY, self.temprotZ, self.temprotTime):
            queue[3].append((rottime, rotx))
            queue[4].append((rottime, roty))
            queue[5].append((rottime, rotz))
            queue[7].append((rottime, math.sqrt(rotx * rotx + roty * roty)))

        # for rotz in self.temprotZ:
        #     queue[5].put(rotz)

        # for time in self.temprotTime:
        #     queue[11].put(time)

        # If new Values, calc a new Integral
        tempZ = not len(self.temprotZ) == 0
        if tempZ:
            queue[9].append(np.trapz(self.calcrotZsmall))

        for step,time in zip(self.tempSteps, self.tempStepsTime):
            queue[8].append((time,step))

        # for time in self.tempStepsTime:
        #     queue[12].put(time)

    def clearTemp(self):
        self.temprotX.clear()
        self.temprotY.clear()
        self.temprotZ.clear()
        self.temprotTime.clear()

        self.tempaccX.clear()
        self.tempaccY.clear()
        self.tempaccZ.clear()
        self.tempaccTime.clear()

        self.tempSteps.clear()
        self.tempStepsTime.clear()

    def save_to_file(self, mes_time, mes_type, v1, v2, v3):
        self.text_file.write('{};{};{};{};{}\n'.format(mes_time, mes_type, v1, v2, v3))