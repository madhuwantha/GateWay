from __future__ import print_function

import keras
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Flatten
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
import numpy as np
import pandas as pd
from keras.utils import to_categorical
from os import path

from Env import Env
from SecurityManagerSDK import SecurityManagerSDK
from mlxtend.evaluate import confusion_matrix
from mlxtend.plotting import plot_confusion_matrix




class FLModel:
    env = Env()

    def __init__(self, epochs):
        """
        :param epochs:
        """
        self._x_train, self._y_train, self._x_val, self._y_val = self._processData()
        self._epochs = epochs
        self._model = None
        self._batch_size = self.env.get(key="batchSize")

    def evaluate(self, x_val, y_val):
        with keras.backend.get_session().graph.as_default():
            if self._model is None:
                self._model = self._buildModel()
            score = self._model.evaluate(x_val, y_val, verbose=0)
            print('Test loss:', score[0])
            print('Test accuracy:', score[1])

    def _processData(self):
        print("Processing LocalData...")
        x = pd.read_csv(self.env.get(key="associationRulesX"))
        y = pd.read_csv(self.env.get(key="associationRulesY"))

        y['0'] = y['0'].replace(['c-SCAN', 'c-LOGIN', 'c-CNC_COM', 'c-MAL_DOWN', 'c-DDOS'], [
            self.env.get(key="c-SCAN"),
            self.env.get(key="c-LOGIN"),
            self.env.get(key="c-CNC_COM"),
            self.env.get(key="c-MAL_DOWN"),
            self.env.get(key="c-DDOS")
        ])
        y = pd.DataFrame(to_categorical(y))

        x_train = x.sample(frac=0.8, random_state=0)
        x_test = x.drop(x_train.index)

        y_train = y.sample(frac=0.8, random_state=0)
        y_test = y.drop(y_train.index)

        print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)
        return x_train, y_train, x_test, y_test

    def _save(self):
        with keras.backend.get_session().graph.as_default():
            self._model = load_model('LocalModel/best_model.h5')
            mod = self._model.get_weights()
            np.save('LocalModel/mod', mod)
            print("Local _model update written to local storage!")

    def _buildModel(self):
        model = None
        with keras.backend.get_session().graph.as_default():
            if path.exists("UpdatedModel/agg_model.h5"):
                print("Agg model exists...\nLoading _model...")
                model = load_model("UpdatedModel/agg_model.h5", compile=False)
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

    def _prob_to_class(self, vector):
        return np.where(vector == np.amax(vector))[0][0]

    def _max_prob(self,vector):
        return np.amax(vector)

    def _evaluate(self):
        y_pred = pd.DataFrame(self._model.predict(self._x_val))
        y_pred['class'] = y_pred.apply(lambda row: self._prob_to_class(row), axis=1)

        result = pd.DataFrame()
        result["pred"] = y_pred['class'].astype(int)
        result["true"] = self._y_val.to_numpy().astype(int)

        cm = confusion_matrix(y_target=result['true'], y_predicted=result['pred'])

        # fig, ax = plot_confusion_matrix(conf_mat=cm, cmap="YlGnBu")

        # report = metrics.classification_report(result['true'], result['pred'], digits=3)
        # print(report)

        return cm



    def train(self):
        with keras.backend.get_session().graph.as_default():
            es = EarlyStopping(monitor='val_acc', mode='max', verbose=1, patience=50)
            mc = ModelCheckpoint('LocalModel/best_model.h5', monitor='val_acc', mode='max',
                                 verbose=1, save_best_only=True)

            if self._model is None:
                self._model = self._buildModel()
            self._model.fit(
                self._x_train,
                self._y_train,
                epochs=self._epochs,
                verbose=0,
                batch_size=self._batch_size,
                validation_data=(self._x_val, self._y_val),
                callbacks=[es, mc]
            )
            self._save()
            smSdk = SecurityManagerSDK()
            smSdk.sendStatus()
            smSdk.senModel()
