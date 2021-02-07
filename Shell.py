import os


class Shell():
    def __init__(self):
        pass

    @staticmethod
    def execute(command):
        os.system(command)

    pass
