import os
# os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"

import matplotlib
import time
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from tkinter import filedialog
import tkinter as tk
import pandas as pd
import math
import numpy as np
from numpy import array
import settings
from queue import Queue
from collections import deque, Counter

from sklearn import metrics
from sklearn.metrics import classification_report
import seaborn as sns


from sklearn.ensemble import RandomForestClassifier
from joblib import dump

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Reshape, GlobalAveragePooling1D, RepeatVector
from keras.layers import Conv2D, MaxPooling2D, Conv1D, MaxPooling1D
from keras.utils import np_utils



FRAMESIZE = settings.FRAMESIZE
STEPSIZE = settings.STEPSIZE
NUM_SUBLABELS = settings.NUM_SUBLABELS
NUM_SENSORS = settings.NUM_SENSORS
NUM_CLASSES = settings.NUM_CLASSES



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

        for index, row in df.iterrows():
            if index < start or index > end:
                df.at[index,'Label'] = 4;

       
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
        magrotXYValues = []
        for index, row in dataframe.iterrows():
            if row['Sensor Type'] == 4:
                rotZValues.append(row['v3'])
                magrotXYValues.append(row['magnitude'])

        rotIntegValues = Queue()
        for i in range(len(rotZValues)):
            sliceRotZ = rotZValues[max(0, i-settings.INTEGRALZFRAMESIZE):min(i+1, len(rotZValues))]
            rotIntegValues.put(np.trapz(sliceRotZ))

        rotXYIntegValues = Queue()
        for i in range(len(magrotXYValues)):
            sliceRotXY = magrotXYValues[max(0, i-settings.INTEGRALXYFRAMESIZE): min(i+1, len(magrotXYValues))]
            rotXYIntegValues.put(np.trapz(sliceRotXY))

        for index, row in dataframe.iterrows():
            if row['Sensor Type'] == 4:
                dataframe.at[index,'rotZInteg'] = rotIntegValues.get()
                dataframe.at[index, 'rotXYInteg'] = rotXYIntegValues.get()

        dataframe.reset_index(inplace=True)

        # print(dataframe[['Sensor Type','v3','rotZInteg']])
        # print("QueueLen: ", rotIntegValues.qsize())



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
    labelqueue = deque(maxlen=framesize*2)

    listSensor = df['Sensor Type'].values
    listMagnitude = df['magnitude'].values
    listv3 = df['v3'].values
    listrotZInteg = df['rotZInteg'].values
    listrotXYInteg = df['rotXYInteg'].values
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
                xyrot.append(listrotXYInteg[counter])
                integRotZ.append(abs(listrotZInteg[counter]))

            if sensortype == 3 or sensortype == 4:
                labelqueue.append(listLabel[counter])

            counter += 1


        if counter < len(df):
            labelstepsize = int(len(labelqueue)/numlabels)
            label = []
            labelqueuelist = list(labelqueue)
            for i in range(0, len(labelqueuelist)-labelstepsize+1, labelstepsize):
                sublabels = labelqueuelist[i:i+labelstepsize]
                data = Counter(sublabels)
                label.append(max(sublabels, key=data.get))

            frames.append([list(xyacc), list(xyrot), list(accZ), list(integRotZ)])
            labels.append(label)
        else:
            break


    framearray = array(frames)
    framearray = np.swapaxes(framearray,1,2)

    labelarray = array(labels)
    # print(framearray)
    # print(labelarray)
    # print(labelarray.shape)


    return framearray, labelarray


def show_confusion_matrix(validations, predictions):

    matrix = metrics.confusion_matrix(validations[:,-1], predictions[:,-1])
    plt.figure(figsize=(6, 4))
    sns.heatmap(matrix,
                cmap="coolwarm",
                linecolor='white',
                linewidths=1,
                xticklabels=settings.LABELS,
                yticklabels=settings.LABELS,
                annot=True,
                fmt="d")
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.show()

model_m = RandomForestClassifier(n_estimators=15, max_depth=4, random_state=0, verbose=True)

def train_this_model(x_train, y_train):

    ### Shuffle
    idx = np.random.permutation(len(x_train))
    x_train, y_train = x_train[idx], y_train[idx]

    callbacks_list = [
        keras.callbacks.ModelCheckpoint(
            filepath='best_model.{epoch:02d}-{val_loss:.2f}.h5',
            monitor='val_loss', save_best_only=True),
        keras.callbacks.EarlyStopping(monitor='acc', patience=4)
    ]

    # model_m = settings.create_model()

    # model_m.compile(loss='categorical_crossentropy',
    #                 optimizer='adam', metrics=['accuracy'])

    # Hyper-parameters
    BATCH_SIZE = 400
    EPOCHS = 50

    #history = model_m.fit(x_train,
                          # y_train,
                          # batch_size=BATCH_SIZE,
                          # epochs=EPOCHS,
                          # callbacks=callbacks_list,
                          # validation_split=0.2,
                          # verbose=1)


    print(x_train.shape)
    print(y_train.shape)
    clf = model_m.fit(x_train, y_train)
    dump(clf, 'tree.joblib')


    # summarize history for accuracy and loss
    # plt.figure(figsize=(6, 4))
    # plt.plot(history.history['acc'], "g--", label="Accuracy of training data")
    # plt.plot(history.history['val_acc'], "g", label="Accuracy of validation data")
    # plt.plot(history.history['loss'], "r--", label="Loss of training data")
    # plt.plot(history.history['val_loss'], "r", label="Loss of validation data")
    # plt.title('Model Accuracy and Loss')
    # plt.ylabel('Accuracy and Loss')
    # plt.xlabel('Training Epoch')
    # plt.ylim(0)
    # plt.legend()
    # plt.grid(b=True, which='major', color='#666666', linestyle='-')
    # plt.show()

def normalize(framearray):

    for frame in framearray:
        maxabs = abs(np.amax(np.absolute(frame), axis=0))
        frame /= settings.DIVISIOR
        # print(frame)
        # frame = min(frame, 1)
        # frame = max(frame, -1)


if __name__ == '__main__':

    root = tk.Tk()
    root.withdraw()

    currdir = os.getcwd()
    file_path = filedialog.askdirectory()

    FileContents = []
    for file in os.listdir(file_path):
        if file.endswith('.csv'):
            FileContents.append(pd.read_csv(os.path.join(file_path,file),delimiter=';'))


    dataframelist = cutFileToSize(FileContents, 100,10)
    createFeatures(dataframelist)

    frames = []
    labels = []

    for dataframe in dataframelist:
        framearray, labelarray = create_frames_and_labels(dataframe, FRAMESIZE, STEPSIZE, NUM_SUBLABELS)
        normalize(framearray)
        frames.append(framearray)
        labels.append(labelarray)
    # np.set_printoptions(threshold=np.nan)

    frames = np.concatenate(frames)

    labels = np.concatenate(labels)
    print('Shape of training frames: ', frames.shape)
    print("Shape of training labels: ", labels.shape)

    #y_train = np_utils.to_categorical(labels, settings.NUM_CLASSES)

    frames = np.reshape(frames, (len(frames), 320))

    y_train = labels
    print("New shape of training labels: ", y_train.shape)
    print(labels[55])
    print(y_train[55])

    ### Shuffle
    idx = np.random.permutation(len(frames))
    x_train, y_train = frames[idx], y_train[idx]

    x_test = x_train[-int(len(x_train) / 10):]
    y_test = y_train[-int(len(y_train) / 10):]

    x_train = x_train[:-int(len(x_train) / 10)]
    y_train = y_train[:-int(len(y_train) / 10)]

    train_this_model(x_train, y_train)

    print("\n--- Confusion matrix for test data ---\n")

    y_pred_test = model_m.predict(x_test)
    # Take the class with the highest probability from the test predictions
    # max_y_pred_test = np.argmax(y_pred_test, axis=1)
    # max_y_test = np.argmax(y_test, axis=1)

    show_confusion_matrix(y_test, y_pred_test)

    ''' Tests
    test_frame = frames[0]
    test_frame = np.reshape(test_frame, (1,80,4))
    model = settings.create_model()
    model.load_weights('model.h5')
    for i in range(1,20):
        millis = int(round(time.time() * 1000))
        prediction = model.predict_classes(test_frame)
        delta = millis = int(round(time.time() * 1000)) - millis
        print(delta)
    '''