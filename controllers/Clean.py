import  os

from controllers.Command import Command


class Clean(Command):
    def images(*args):
        print("Removing dangling docker images")
        os.system("docker rmi $(docker images -qa -f 'dangling=true')")

    def cache(*args):
        print("Deleting docker build cache")
        os.system("docker builder prune -a")

    def terminating(*args):
        print("Forcing deleting pods stuck in \"Terminating\" status")
        os.system("for p in $(kubectl get pods | grep Terminating | awk '{print $1}'); do kubectl delete pod $p --grace-period=0 --force;done")