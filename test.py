import efficient_apriori 
import numpy as np
import pandas as pd

def data_generator(filename):
  """
  Data generator, needs to return a generator to be called several times.
  """
  def data_gen():
    with open(filename) as file:
      for line in file:
        yield tuple(k.strip() for k in line.split(','))

  return data_gen

transactions = data_generator('/home/tf/GateWay/tmp/pycharm_project_459/UpdatedAnomali/preprocessed.csv')
itemsets, rules = efficient_apriori.apriori(transactions, min_support=0.00015, min_confidence=0.001, verbosity=1)
print(type(itemsets))
print(type(rules))


it = pd.DataFrame(itemsets)
it.to_csv("itemsets.csv")

ru = np.array(rules)
ru = pd.DataFrame(ru)
ru.to_csv("rule.csv")
