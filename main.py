from Env import Env

from FIM import FIM
# from Server import run
from FLModel import FLModel

from Server import run


def flaskThread():
    run()


if __name__ == '__main__':
    print("program Starting.....")
    env = Env()

    # run()

    # TODO: run anomaly

    fim = FIM()
    x_, y_, rules_ = fim.getFrequentItemset()

    # TODO:  model train

    # fl = FLModel(epochs=env.get(key="epochs"))
    # fl.train()
