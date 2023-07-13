import sys, os, subprocess

from utils import label_deployment, filter_services
from controllers.Command import Command, action


class Service(Command):
    @action()
    def index(self, *args):
        print("INDEX")

    @action(ignore_services=True)
    def list(self, *args):
        for service in self.project.services:
            print(service.name)

    @action()
    def exposed(self, services: list):
        services = filter_services(services, "exposeable")
        for service in services:
            os.system(f"minikube service {service.k8s_service_name}")
                
    @action()
    def expose(self, services: list):
        services = filter_services(services, "exposeable")
        for service in services:
            os.system(f"minikube service --url {service.k8s_service_name}")

    # Burndown, build, push, then burnup services
    @action()
    def rebuild(self, services):
        self._down(services)
        services = filter_services(services, "buildable")
        for service in services:
            self._docker_build(service, prune=True)
            self._docker_push(service)
        
        self._up(services)

    @action()
    def exec(self, services):
        if len(services) > 1:
            print("You can only watch one service at a time")

        service = services[0]

        print(f"Exec(ing) into {service.name}")
        os.system(f"service=\"$(kubectl get pods --no-headers -o custom-columns=':metadata.name' | grep {service.k8s_deployment_name})\" && kubectl exec --stdin --tty $service -- /bin/bash")

    @action()
    def watch(self, services):
        if len(services) == 0:
            print("You must provide a service to watch")
            sys.exit(1)

        if len(services) > 1:
            print("You can only watch one service at a time")

        service = services[0]

        print(f"Watching pod logs for the {service.name} deployment")
        os.system(f"service=\"$(kubectl get pods --no-headers -o custom-columns=':metadata.name' | grep {self.project.name}-{service.name}-deployment)\" && kubectl logs -f $service")

    # Burndown services
    @action()
    def down(self, services):
        self._down(services)

    def _down(self, services):
        if len(services) == 0:
            subprocess.run(self.project.burndown)
            return

        for service in services:
            subprocess.run(f"{service.deploy_dir}local/minikube/burndown")

    # Burnup services
    @action()
    def up(self, services):
        self._up(services)

    def _up(self, services):
        if len(services) == 0:
            subprocess.run(self.project.burnup)
            return

        for service in services:
            subprocess.run(f"{service.deploy_dir}local/minikube/burnup")

    # Burndown then burnup services
    @action()
    def restart(self, services):
        if len(services) == 0:
            subprocess.run(f"{self.pwd}burndown")
            subprocess.run(f"{self.pwd}burnup")
            return
            
        self._down(services)
        self._up(services)

    @action()
    def build(self, services):
        self._down(services)
        for service in services:
            if not getattr(service, "buildable", False):
                print(f"Service {service.name} is not buildable")
                continue
            
            self._docker_build(service, prune=True)
        self._up(services)

    @action()
    def buildp(self, services):
        for service in services:
            if not getattr(service, "buildable", False):
                print(f"Service {service.name} is not buildable")
                continue
            
            self._docker_build(service, prune=True)
            self._docker_push(service)

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