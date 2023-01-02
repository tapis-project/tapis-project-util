import json, sys, os, subprocess

from types import SimpleNamespace

from utils import label_deployment, get_name_version
from constants import CATEGORIES
from controllers.Command import Command


def action(fn):
    def wrapper(self, *args, **_):
        try:
            with open(self.config_path, "r") as f:
                self.project = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

                # Set project defaults
                scripts = getattr(self.project, "scripts", {})
                self.project.burndown = getattr(scripts, "burndown", f"{self.pwd}burndown")
                self.project.burnup = getattr(scripts, "burnup", f"{self.pwd}burnup")
        except Exception as e:
            print(e)
            raise Exception("Missing tapis-project.json: You are not in an initialized tapis project")

        category = args[0]
        if category not in CATEGORIES:
            raise Exception(f"Unrecognized category '{category}'. Expected one of {CATEGORIES}")

        service_names = args[1:]
        if len(service_names) < 1:
            raise Exception("Must provide at least one service")

        services = []
        for service_name in service_names:
            name, version = get_name_version(service_name)

            # List of services upon which the action will be taken
            service = next(filter(lambda service: service.name == name, getattr(self.project.categories, category)), None)
            if service == None:
                raise Exception(f"'{name}' is not a valid service")
            
            # Configure the default settings for the service
            service.version = version or getattr(service, "defaultVersion", "latest")
            service.image = getattr(service, "image", f"tapis/{self.project.name}-{service.name}")
            service.versioned_image = service.image + f":{service.version}"
            service.root_dir = getattr(service, "rootDir", f"{self.pwd}src/{service.name}/src/")
            service.build_path = getattr(service, "buildPath", service.root_dir)
            service.deploy_dir = getattr(service, "deployDir", f"{self.pwd}src/{service.name}/deploy/")
            service.dockerfile_path = getattr(service, "dockerfilePath", f"{service.root_dir}Dockerfile")
            service.k8s_service_name = getattr(service, "k8sServiceName", f"{self.project.name}-{service.name}-service")
            service.k8s_deployment_name = getattr(service, "k8sDeploymentName", f"{self.project.name}-{service.name}-deployment")
            services.append(service)

        return fn(self, services, **_)

    return wrapper

class Index(Command):
    @action
    def index(self):
        print("INDEX")

    @action
    def system_start(self, node_count, *args):
        os.system(f"minikube start --nodes {node_count}")

    @action
    def system_stop(self, *args):
        os.system(f"minikube stop")

    @action
    def dashboard(self, *args):
        os.system("minikube dashboard")

    def _filter_services(self, services: list, key: str):
        for service in services:
            if not getattr(service, key, False):
                print(f"Service {service.name} is not {key}")
                services.remove(service)
        
        return services

    @action
    def exposed(self, services: list):
        services = self._filter_services(services, "exposeable")
        for service in services:
            os.system(f"minikube service {service.k8s_service_name}")
                
    @action
    def expose(self, services: list):
        services = self._filter_services(services, "exposeable")
        for service in services:
            os.system(f"minikube service --url {service.k8s_service_name}")

    # Burndown, build, push, then burnup services
    @action
    def rebuild(self, services):
        self._down(services)
        services = self._filter_services(services, "buildable")
        for service in services:
            self._docker_build(service, prune=True)
            self._docker_push(service)
        
        self._up(services)

    @action
    def exec(self, services):
        if len(services) > 1:
            print("You can only watch one service at a time")

        service = services[0]

        print(f"Exec(ing) into {service.name}")
        os.system(f"service=\"$(kubectl get pods --no-headers -o custom-columns=':metadata.name' | grep {service.k8s_deployent_name})\" && kubectl exec --stdin --tty $service -- /bin/bash")

    @action
    def watch(self, services):
        if len(services) == 0:
            print("You must provide a service to watch")
            sys.exit(1)

        if len(services) > 1:
            print("You can only watch one service at a time")

        service = services[0]

        print(f"Watching pod logs for the {service.name} deployment")
        os.system(f"service=\"$(kubectl get pods --no-headers -o custom-columns=':metadata.name' | grep {self.project.name}-{service.name}-deployment)\" && kubectl logs -f $service")

    @action
    def clean(*args):
        args = args[0]
        if "images" in args:
            print("Removing dangling docker images")
            os.system("docker rmi $(docker images -qa -f 'dangling=true')")

        if "cache" in args:
            print("Deleting docker build cache")
            os.system("docker builder prune -a")

        if "terminating" in args:
            print("Forcing deleting pods stuck in \"Terminating\" status")
            os.system("for p in $(kubectl get pods | grep Terminating | awk '{print $1}'); do kubectl delete pod $p --grace-period=0 --force;done")



    # Burndown services
    @action
    def down(self, services):
        self._down(services)

    def _down(self, services):
        if len(services) == 0:
            subprocess.run(self.project.burndown)
            return

        for service in services:
            subprocess.run(f"{service.deploy_dir}local/minikube/burndown")

    # Burnup services
    @action
    def up(self, services):
        self._up(services)

    def _up(self, services):
        if len(services) == 0:
            subprocess.run(self.project.burnup)
            return

        for service in services:
            subprocess.run(f"{service.deploy_dir}local/minikube/burnup")

    # Burndown then burnup services
    @action
    def restart(self, services):
        if len(services) == 0:
            subprocess.run(f"{self.pwd}burndown")
            subprocess.run(f"{self.pwd}burnup")
            return
            
        self._down(services)
        self._up(services)

    @action
    def build(self, services):
        self._down(services)
        for service in services:
            if not getattr(service, "buildable", False):
                print(f"Service {service.name} is not buildable")
                continue
            
            self._docker_build(service, prune=True)
        self._up(services)

    def _docker_prune(self, label):
        return f"docker image prune --force --filter='label={label}'"

    def _docker_build(self, service, prune=False):
        label = label_deployment(self.project, service)
        prune = f"&& {self._docker_prune(label)}" if prune else ""
        cmd = f"docker build -t {service.versioned_image} --label {label} -f {service.dockerfile_path} {service.build_path} {prune}"
        os.system(cmd)

    def _docker_push(self, service):
        cmd = f"docker push {service.versioned_image}"
        print("CMD", cmd)
        os.system(cmd)