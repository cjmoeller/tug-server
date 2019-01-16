import os
from tkinter import filedialog
import tkinter as tk
import pandas as pd
import math
import numpy as np
import settings
from queue import Queue



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

        print(dataframe[['Sensor Type','v3','rotZInteg']])
        print("QueueLen: ", rotIntegValues.qsize())
        break




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