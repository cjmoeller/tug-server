import os
os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Reshape, GlobalAveragePooling1D, RepeatVector
from keras.layers import Conv2D, MaxPooling2D, Conv1D, MaxPooling1D
from keras.utils import np_utils


RABBITMQ = "192.168.178.25"

FRAMESIZE = 80
STEPSIZE = 1
NUM_SUBLABELS = 10  # Should evenly devide the framesize!
NUM_SENSORS = 4
NUM_CLASSES = 4

PLOTTINGFRAMESIZE = FRAMESIZE*5

INTEGRALZFRAMESIZE = 40
INTEGRALXYFRAMESIZE = 75

MODEL = "best_model.50-0.09.h5"

LASTPREDICTION = 0


def create_model():
    model_m = Sequential()
    model_m.add(Conv1D(100, 10, activation='relu', input_shape=(FRAMESIZE, NUM_SENSORS)))
    model_m.add(Conv1D(100, 10, activation='relu'))
    model_m.add(MaxPooling1D(3))
    model_m.add(Conv1D(160, 11, activation='relu'))
    model_m.add(Dropout(0.5))
    model_m.add(Dense(200, activation='sigmoid'))
    model_m.add(Dense(80, activation='sigmoid'))
    model_m.add(Dense(NUM_CLASSES, activation='softmax'))
    return model_m


def init():
    global keyboardLabel
    keyboardLabel = 0