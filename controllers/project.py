import os, sys, json

from constants import BASE_DIR
from controllers.Command import Command

class Project(Command):
    def create(self):
        if os.path.isfile(self.config_path):
            print("Project already initialized")
            sys.exit(0)

        self.project = None

        try:
            with open(f"{BASE_DIR}/project-template.json", "r") as f:
                self.project = json.load(f)
        except Exception:
            print("Missing project-template.json. Cannot initialize package")
            sys.exit(1)

        with open(self.config_path, "w") as f:
            json.dump(self.project, f, indent=4)