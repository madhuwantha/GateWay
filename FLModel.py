from __future__ import print_function

import keras
from keras.datasets import mnist
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
import numpy as np
import pandas as pd
import glob
from os import path

from SecurityManagerSDK import SecurityManagerSDK


class FLModel:
    def __init__(self, epochs):
        """
        :param epochs:
        """
        self._x_train, self._y_train, self._x_val, self._y_val = self._processData()
        self._epochs = epochs
        self._model = None

    def evaluate(self, x_val, y_val):
        if self._model is None:
            self._model = self._buildModel()
        score = self._model.evaluate(x_val, y_val, verbose=0)
        print('Test loss:', score[0])
        print('Test accuracy:', score[1])

    def _splitData(self, data):
        """
        Set the _x_train, _y_train, _x_val, _y_val
        :param data: One-Hot encoded pandas DataFrame
        """
        # TODO : Implementation
        pass

    def _processData(self):
        print("Processing LocalData...")
        x = pd.read_csv('LocalData/x_train.csv')
        y = pd.read_csv('LocalData/y_train.csv')
        x_train = x.sample(frac=0.8, random_state=0)
        x_test = x.drop(x_train.index)

        y_train = y.sample(frac=0.8, random_state=0)
        y_test = y.drop(y_train.index)

        print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)
        return x_train, y_train, x_test, y_test

    def _save(self):
        mod = self._model.get_weights()
        np.save('LocalModel/mod', mod)
        print("Local _model update written to local storage!")

    def _buildModel(self):
        model = None
        if path.exists("UpdatedModel/aggModel.h5"):
            print("Agg _model exists...\nLoading _model...")
            model = load_model("UpdatedModel/aggModel.h5")
        else:
            print("No agg _model found!\nBuilding _model...")
            model = Sequential()
            model.add(Dense(units=200, activation='relu', input_shape=[len(self._x_train.columns)]))
            model.add(Dense(500, activation='relu'))
            model.add(Dropout(0.8))
            model.add(Dense(1000, activation='relu'))
            model.add(Dropout(0.7))
            model.add(Dense(400, activation='relu'))
            model.add(Dropout(0.8))
            model.add(Dense(len(self._y_train.columns), activation='softmax'))

        model.compile(loss=keras.losses.categorical_crossentropy, optimizer=keras.optimizers.Adadelta(),
                      metrics=['accuracy'])

        return model

    def train(self):
        if self._model is None:
            self._model = self._buildModel()
        self._model.fit(self._x_train, self._y_train, epochs=self._epochs, verbose=1,
                        batch_size=500,
                        validation_data=(self._x_val, self._y_val))
        self._save()
        SecurityManagerSDK.sendStatus()
