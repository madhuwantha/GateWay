import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import association_rules
import FIMFunctions
from Env import Env


class FIM:
    def __init__(self):
        self._env = Env()
        self._dataSet = None

    def _freqItemsetMining(self):
        y = None
        print("Starting FIM")

        print("Transaction Encoder is started")
        te = TransactionEncoder()
        te_ary = te.fit(self._dataSet.to_numpy()).transform(self._dataSet.to_numpy())
        transformed_df = pd.DataFrame(te_ary, columns=te.columns_)
        print("Transaction Encoder is finished")
        print("Apriori is started")

        freqItemsets = apriori(transformed_df, min_support=float(self._env.get(key="minSupport")), use_colnames=True)
        print("Saving Frequent Itemsets...")
        freqItemsets.to_csv(self._env.get(key="freqItemFilePath"))
        print("Frequent Itemsets Saved")

        print("Apriori is finished")
        print("Association rules mining is started")
        rules = association_rules(freqItemsets, metric=self._env.get(key="ruleMetric"),
                                  min_threshold=float(self._env.get(key="minSupport")))
        rules = rules[(rules['consequents'] == {self._env.get(key="c1")}) |
                      (rules['consequents'] == {self._env.get(key="c2")}) |
                      (rules['consequents'] == {self._env.get(key="c3")}) |
                      (rules['consequents'] == {self._env.get(key="c4")}) |
                      (rules['consequents'] == {self._env.get(key="c5")}) &
                      ((self._env.get(key="c1") not in (rules.antecedents.to_list())) |
                       (self._env.get(key="c2") not in (rules.antecedents.to_list())) |
                       (self._env.get(key="c3") not in (rules.antecedents.to_list())) |
                       (self._env.get(key="c4") not in (rules.antecedents.to_list())) |
                       (self._env.get(key="c5") not in (rules.antecedents.to_list()))
                       )]
        rules['antecedents'] = rules.apply(
            lambda row: FIMFunctions.convertToStringList(str(list(row['antecedents']))),
            axis=1)
        rules['consequents'] = rules.apply(
            lambda row: FIMFunctions.convertToStringList(str(list(row['consequents']))),
            axis=1)
        rules.reset_index(inplace=True)

        print("Association rules mining is finished")

        print("One Hot encoding is started")
        cols = self._dataSet.columns[:-1]
        print(cols)
        featureList = [self._env.get(key="p-tcp"), self._env.get(key="p-http"), self._env.get(key="p-ssh"),
                       self._env.get(key="p-dns"), self._env.get(key="p-ftp"), self._env.get(key="p-sshv2"),
                       self._env.get(key="l0"), self._env.get(key="l1"), self._env.get(key="l2"), self._env.get(key="l3"),
                       # self._env.get(key="r-public"), self._env.get(key="r-private"), self._env.get(key="r-non"),
                       self._env.get(key="c1"), self._env.get(key="c2"), self._env.get(key="c3"),
                       self._env.get(key="c4"), self._env.get(key="c5"), self._env.get(key="d1"),
                       self._env.get(key="d2"), self._env.get(key="d3"), self._env.get(key="d4"),
                       self._env.get(key="d5"), self._env.get(key="d6"), self._env.get(key="d7"),
                       self._env.get(key="d8"), self._env.get(key="d9"), self._env.get(key="d10")]

        x = pd.DataFrame(FIMFunctions.oneHot(rules, featureList), columns=featureList)
        if len(x) > 0:
            y = rules.apply(
                lambda row: str(row["consequents"][0].replace('[', '').replace(']', '')),
                axis=1)

        return x, y, rules

    def getFrequentItemset(self):
        print("Load data Set")
        self._dataSet = pd.read_csv(self._env.get(key="dataFilePath"))

        print("Start Pre-processing")
        self._dataSet = FIMFunctions.preProcessing(self._dataSet)
        print("End pre-processing")

        print("Assigning Classes")
        self._dataSet = FIMFunctions.assign_class(self._dataSet, self._env.get(key="botIP"), self._env.get(key="cncIP"),
                                                  self._env.get(key="victimIP"), self._env.get(key="loaderIP"))
        print("Classes are assigned")

        self._dataSet.to_csv('preprocessed.csv')

        x_, y_, rules_ = self._freqItemsetMining()

        print("Saving Results...")
        x_.to_csv(self._env.get(key="associationRulesX"))
        y_.to_csv(self._env.get(key="associationRulesY"))
        rules_.to_csv(self._env.get(key="associationRules"))
        print("Results Saved")

        return x_, y_, rules_
