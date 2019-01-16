import os
from tkinter import filedialog
import tkinter as tk
import pandas as pd



def cutFileToSize(FileContents, valsBefore, valsAfter):
    '''
    Turns pandas Files into pandas Dataframes and cuts them to size
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


if __name__ == '__main__':

    root = tk.Tk()
    root.withdraw()

    currdir = os.getcwd()
    file_path = filedialog.askdirectory()

    FileContents = []
    for file in os.listdir(file_path):
        if file.endswith('.csv'):
            FileContents.append(pd.read_csv(os.path.join(file_path,file),delimiter=';'))

    print(cutFileToSize(FileContents, 10,10))