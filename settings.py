import os
# os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"

from collections import deque

import keras
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Reshape, GlobalAveragePooling1D, RepeatVector
from keras.layers import Conv2D, MaxPooling2D, Conv1D, MaxPooling1D
from keras.utils import np_utils


RABBITMQ = "localhost"

FRAMESIZE = 80
STEPSIZE = 1
NUM_SUBLABELS = 10  # Should evenly devide the framesize!
NUM_SENSORS = 4
NUM_CLASSES = 5

PLOTTINGFRAMESIZE = FRAMESIZE*5

INTEGRALZFRAMESIZE = 40
INTEGRALXYFRAMESIZE = 75

MODEL = "best_model.46-0.32.h5"

LASTPREDICTION = deque(maxlen=5)

DIVISIOR = (24,200,20,200)


def create_model():
    model_m = Sequential()
    model_m.add(Conv1D(10, 10, activation='relu', input_shape=(FRAMESIZE, NUM_SENSORS)))
    model_m.add(Conv1D(50, 10, activation='relu'))
    model_m.add(MaxPooling1D(3))
    model_m.add(Conv1D(100, 11, activation='relu'))
    model_m.add(Dropout(0.3))
    model_m.add(Dense(80, activation='sigmoid'))
    model_m.add(Dense(40, activation='sigmoid'))
    model_m.add(Dense(NUM_CLASSES, activation='softmax'))

    print(model_m.summary())

    return model_m


def init():
    global keyboardLabel
    keyboardLabel = 0