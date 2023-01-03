import os
from controllers.Command import Command, action


class System(Command):
    @action(ignore_services=True)
    def index(self):
        print("INDEX")

    @action(ignore_services=True)
    def start(self, node_count, *args):
        os.system(f"minikube start --nodes {node_count}")

    @action(ignore_services=True)
    def stop(self, *args):
        os.system(f"minikube stop")

    @action(ignore_services=True)
    def dashboard(self, *args):
        os.system("minikube dashboard")