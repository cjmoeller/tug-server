import os
import matplotlib
matplotlib.use("TkAgg")
from tkinter import filedialog
import tkinter as tk
import pandas as pd
import math
import numpy as np
from numpy import array
import settings
from queue import Queue
from collections import deque, Counter




def cutFileToSize(FileContents, valsBefore, valsAfter):
    '''
    Turns pandas Files into pandas Dataframes and cuts them to size
    FileContents: Content of csv File
    valsBefore: How many values you want to keep before the first '1' Label
    valsAfter: How many Values you want to keep after the last '3' Label
    '''
    dataFrameList = []
    for file in FileContents:
        df = pd.DataFrame(file, columns = ['time','Sensor Type','v1','v2','v3','Label'])

        labelList = df['Label'].tolist()
        start = labelList.index(1)
        end = len(labelList) - 1 - labelList[::-1].index(3)
       
        if (start -valsBefore >= 0) and (end + valsAfter < len(labelList)):
            start = start -valsBefore
            end = end + valsAfter
        else:
            print ("List of vals to short")
            os._exit(0)

        dataFrameList.append(df[start:end])
    return dataFrameList


def createFeatures(dataFrameList):


    for dataframe in dataFrameList:
        dataframe['magnitude'] = dataframe.apply(lambda row: math.sqrt(row.v1 * row.v1 + row.v2 * row.v2), axis=1)


        rotZValues = []
        for index, row in dataframe.iterrows():
            if row['Sensor Type'] == 4:
                rotZValues.append(row['v3'])

        rotIntegValues = Queue()
        for i in range(len(rotZValues)):
            slice = rotZValues[max(0, i-settings.INTEGRALFRAMESIZE):min(i+1, len(rotZValues))]
            rotIntegValues.put(np.trapz(slice))

        for index, row in dataframe.iterrows():
            if row['Sensor Type'] == 4:
                dataframe.at[index,'rotZInteg'] = rotIntegValues.get()

        dataframe.reset_index(inplace=True)

        # print(dataframe[['Sensor Type','v3','rotZInteg']])
        # print("QueueLen: ", rotIntegValues.qsize())
        break


def create_frames_and_labels(df, framesize, stepsize, numlabels):

    '''
    :param dataframe: Die zu trainierenden Werte
    :param framesize: Die Größe eines gleichzeitig betrachteten Frames
    :param stepsize: Die Verschiebung des Frames über die Zeitreihe
    :param numlabels: Die Anzahl der gleichmäßig verteilten Label auf einem Frame
    :return:
    '''


    num_features = 4 # magXY für Rot und Acc, IntegRotZ und AccZ
    frames = []
    labels = []

    xyacc = deque(maxlen=framesize)
    xyrot = deque(maxlen=framesize)
    accZ = deque(maxlen=framesize)
    integRotZ = deque(maxlen=framesize)
    labelqueue = deque(maxlen=framesize*num_features)

    listSensor = df['Sensor Type'].values
    listMagnitude = df['magnitude'].values
    listv3 = df['v3'].values
    listrotZInteg = df['rotZInteg'].values
    listLabel = df['Label'].values

    counter = 0
    c3 = 0
    c4 = 0
    while True:

        count3 = 0
        count4 = 0


        while (count3 < stepsize or count4 < stepsize or c3 < framesize or c4 < framesize) and counter < len(df):
            sensortype = listSensor[counter]

            if sensortype == 3:
                count3 += 1
                c3 += 1
                xyacc.append(listMagnitude[counter])
                accZ.append(listv3[counter])
            elif sensortype == 4:
                count4 += 1
                c4 += 1
                xyrot.append(listMagnitude[counter])
                integRotZ.append(listrotZInteg[counter])

            if sensortype == 3 or sensortype == 4:
                labelqueue.append(listLabel[counter])

            counter += 1


        if counter < len(df):
            labelstepsize = int(len(labelqueue)/numlabels)
            label = []
            labelqueuelist = list(labelqueue)
            for i in range(0, len(labelqueue)-labelstepsize, labelstepsize):
                sublabels = labelqueuelist[i:i+labelstepsize]
                data = Counter(sublabels)
                label.append(max(sublabels, key=data.get))

            frames.append([list(xyacc), list(xyrot), list(accZ), list(integRotZ)])
            labels.append(label)
        else:
            print(frames)
            break

    framearray = array(frames)
    print(framearray.shape)


if __name__ == '__main__':

    root = tk.Tk()
    root.withdraw()

    currdir = os.getcwd()
    file_path = filedialog.askdirectory()

    FileContents = []
    for file in os.listdir(file_path):
        if file.endswith('.csv'):
            FileContents.append(pd.read_csv(os.path.join(file_path,file),delimiter=';'))


    dataframelist = cutFileToSize(FileContents, 10,10)
    createFeatures(dataframelist)
    create_frames_and_labels(dataframelist[0], 80, 10, 10)