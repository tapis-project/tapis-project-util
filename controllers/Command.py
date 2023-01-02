import os


class Command:
    def __init__(self,):
        self.pwd = os.getcwd() + "/"
        self.config_path = f"{self.pwd}tapis-project.json"
        self.project = None