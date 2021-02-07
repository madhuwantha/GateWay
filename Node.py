class Node(object):
    def __init__(self, k, d):
        self.key = k
        self.data = d

    def __str__(self):
        return "(" + str(self.key) + ", " + str(self.data) + ")"
