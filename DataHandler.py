import time, threading
import struct
import math
import numpy as np
from collections import deque

class DataHandler(threading.Thread):

    SMALLERFRAME = 100

    def __init__(self, queue, queueList):
        threading.Thread.__init__(self)
        self.queue = queue

        #### Useable Vars
        self.accX, self.accY, self.accZ = queueList[0:3]
        self.rotX, self.rotY, self.rotZ = queueList[3:6]
        self.accXY, self.rotXY, self.steps, self.integRotZ = queueList[6:10]

        print("start")


    def run(self):

        #### Temp filler Vars
        self.tempaccX = deque()
        self.tempaccY = deque()
        self.tempaccZ = deque()

        self.temprotX = deque()
        self.temprotY = deque()
        self.temprotZ = deque()

        self.tempSteps = deque()

        self.calcrotZsmall = deque(maxlen=self.SMALLERFRAME)

        for body in iter(self.queue.get, None):
            print(' [x] received %r' % (body,))
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

            self.tempaccX.append(float(v1))
            self.tempaccY.append(float(v2))
            self.tempaccZ.append(float(v3))

        if measurement_type == 4:
            time = struct.unpack('>q', body[1:9])[0]

            v4 = struct.unpack('>f', body[9:13])[0]
            v5 = struct.unpack('>f', body[13:17])[0]
            v6 = struct.unpack('>f', body[17:21])[0]

            self.temprotX.append(float(v4))
            self.temprotY.append(float(v5))
            self.temprotZ.append(float(v6))

        if measurement_type == 5:
            time = struct.unpack('>q', body[1:9])[0]
            steps = struct.unpack('>f', body[9:13])[0]

            self.tempSteps.append(float(steps))


    def tuneValues(self):
        for accx, accy in zip(self.tempaccX, self.tempaccY):
            self.accX.append(accx)
            self.accY.append(accy)
            self.accXY.append(math.sqrt(accx * accx + accy * accy))

        for accz in self.tempaccZ:
            self.accZ.append(accz)


        for rotx, roty in zip(self.temprotX, self.temprotY):
            self.rotX.append(rotx)
            self.rotY.append(roty)
            self.rotXY.append(math.sqrt(rotx * rotx + roty * roty))

        tempZ = not len(self.temprotZ) == 0
        for rotz in self.temprotZ:
            self.rotZ.append(rotz)
            self.calcrotZsmall.append(rotz)

        # If new Values, calc a new Integral
        if tempZ:
            self.integRotZ.append(np.trapz(self.calcrotZsmall))

        for step in self.tempSteps:
            self.steps.append(step)


    def clearTemp(self):
        self.temprotX.clear()
        self.temprotY.clear()
        self.temprotZ.clear()

        self.tempaccX.clear()
        self.tempaccY.clear()
        self.tempaccZ.clear()

        self.tempSteps.clear()