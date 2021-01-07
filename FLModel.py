from __future__ import print_function

import keras
from keras.datasets import mnist
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
import numpy as np
import glob
from os import path

from SecurityManagerSDK import SecurityManagerSDK


class FLModel(object):
    def __init__(self, data, epochs) -> None:
        """
        :param data: One-Hot encoded pandas DataFrame
        :param epochs:
        """
        self.x_train, self.y_train, self.x_val, self.y_val = None, None, None, None
        self.epochs = epochs
        self._splitData(data)
        self.model = None

    def tarin(self):
        if self.model is None:
            self.model = self._buildModel()
        self.model.fit(self.x_train, self.y_train, epochs=self.epochs, verbose=1, validation_data=(self.x_val, self.y_val))
        self._save()
        SecurityManagerSDK.sendStatus()

    def evaluate(self, x_val, y_val):
        if self.model is None:
            self.model = self._buildModel()
        score = self.model.evaluate(x_val, y_val, verbose=0)
        print('Test loss:', score[0])
        print('Test accuracy:', score[1])

    def _splitData(self, data):
        """
        Set the x_train, y_train, x_val, y_val
        :param data: One-Hot encoded pandas DataFrame
        """
        # TODO : Implementation
        pass

    def _save(self):
        mod = self.model.get_weights()
        np.save('LocalModel/mod', mod)
        print("Local model update written to local storage!")

    def _buildModel(self):
        if path.exists("UpdatedModel/aggModel.h5"):
            print("Agg model exists...\nLoading model...")
            model = load_model("UpdatedModel/aggModel.h5")
            return model
        else:
            print("No agg model found!\nBuilding model...")
            model = Sequential()
            model.add(Dense(units=200, activation='relu', input_shape=[len(self.x_train)]))
            model.add(Dense(200, activation='relu'))
            model.add(Dense(5, activation='softmax'))

            model.compile(loss=keras.losses.categorical_crossentropy, optimizer=keras.optimizers.Adadelta(),
                          metrics=['accuracy'])

            return model
