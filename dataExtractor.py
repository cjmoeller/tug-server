import os
from tkinter import filedialog
import tkinter as tk
import pandas as pd

def createnewFile(file, path, LabelNmbr):
    filename = file
    filename = filename.replace('.csv','')
    fileNmbr = 0
    filename =filename+"-Label-"+str(LabelNmbr)+'-'+str(fileNmbr)


    if(os.path.isfile(os.path.join(newpath,filename)+'.csv')): #Für den Fall, dass ein File bereits existiert, bzw. der Filename breits vergeben ist
        return


    '''
    #
    #Vielleicht ist das ja noch nützlich.
    #Generiert neue Filenames, bis es kein File mit dem aktullen Namen gibt. (Zählt die Variable fileNmbr hoch)
    #

    while(os.path.isfile(os.path.join(newpath,filename)+'.csv')):
        print('file name already exists')
        filename = filename[:-len(str(fileNmbr))]
        fileNmbr +=1
        filename = filename+str(fileNmbr) 
    '''

    print('Creating File for Label: '+str(LabelNmbr))
    text_file = open(os.path.join(newpath, filename)+'.csv', "w+")
    text_file.write("time;Sensor Type;v1;v2;v3;Label\n")
    
    return text_file

def exportData(dirPath,file, newpath):


    fileLabel1 = createnewFile(file,newpath, 1)
    fileLabel2 = createnewFile(file,newpath, 2)
    fileLabel3 = createnewFile(file,newpath, 3)

    if (fileLabel1 is None) or (fileLabel2 is None) or (fileLabel3 is None):
        print('File wit name {} already exists! Aborting Mission.'.format(file))
        return


    contents = pd.read_csv(os.path.join(dirPath,file),delimiter=';')
    df = pd.DataFrame(contents, columns = ['time','Sensor Type','v1','v2','v3','Label'])
    for row in df.iterrows():

        Time =row[1]['time']
        SensorType =row[1]['Sensor Type']
        v1 =row[1]['v1']
        v2 =row[1]['v2']
        v3 =row[1]['v3']
        Label =row[1]['Label']

        if(row[1]['Label'] == 1):
            fileLabel1.write('{};{};{};{};{};{}\n'.format(Time,SensorType,v1,v2,v3,Label))
        elif(row[1]['Label'] == 2):
            fileLabel2.write('{};{};{};{};{};{}\n'.format(Time,SensorType,v1,v2,v3,Label))
        elif(row[1]['Label'] == 3):
            fileLabel3.write('{};{};{};{};{};{}\n'.format(Time,SensorType,v1,v2,v3,Label))

if __name__ == '__main__':

    root = tk.Tk()
    root.withdraw()
    currdir = os.getcwd()
    file_path = filedialog.askdirectory()
    newpath = os.path.join(file_path,'extractedData')
    print(file_path)
    print('newpath: {}'.format(newpath))

    if not os.path.exists(newpath):
        print('Creating new directory for Labels')
        os.makedirs(newpath)
    else:
        print('Directory already exists!')

    for file in os.listdir(file_path):
        if file.endswith('.csv'):
            print('Exporting Data from {}'.format(file))
            exportData(file_path, file, newpath)

