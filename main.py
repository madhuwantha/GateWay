from Env import Env

from FIM import FIM

if __name__ == '__main__':
    print("program Starting.....")
    env = Env()

    # run()

    # TODO: run anomaly

    fim = FIM()

    # for i in range(1, 5000, 100):
    #     x_, y_, rules_ = fim.getFrequentItemset(minConf=i/10000)

    x_, y_, rules_ = fim.getFrequentItemset()


    # TODO:  model train

    # fl = FLModel(epochs=env.get(key="epochs"))
    # fl.train()
