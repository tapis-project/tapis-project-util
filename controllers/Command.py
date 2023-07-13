import json, os, sys

from types import SimpleNamespace

from utils import get_name_version

def initialize_controller(controller):
    try:
        with open(controller.config_path, "r") as f:
            controller.project = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

            # Set project defaults
            scripts = getattr(controller.project, "scripts", {})
            controller.project.burndown = getattr(scripts, "burndown", f"{controller.pwd}burndown")
            controller.project.burnup = getattr(scripts, "burnup", f"{controller.pwd}burnup")

        return controller
    except Exception:
        print("Missing tapis-project.json: You are not in an initialized tapis project")
        sys.exit(1)

def action(ignore_services=False):
    def inner(fn):
        def wrapper(controller, *args, **_):
            controller = initialize_controller(controller)
            
            if ignore_services:
                return fn(controller, *args, **_)
            
            service_names = args[0:]
            if len(service_names) < 1:
                raise Exception("Must provide at least one service")

            services = []
            for service_name in service_names:
                name, version = get_name_version(service_name)

                # List of services upon which the action will be taken
                service = next(filter(lambda service: service.name == name, controller.project.services), None)
                if service == None:
                    raise Exception(f"'{name}' is not a valid service")

                # Configure the default settings for the service
                service.version = version or getattr(service, "defaultVersion", "latest")
                service.image = getattr(service, "image", f"tapis/{controller.project.name}-{service.name}")
                service.versioned_image = service.image + f":{service.version}"
                service.root_dir = getattr(service, "rootDir", f"{controller.pwd}src/{service.name}/src/")
                service.build_path = "."
                service.deploy_dir = getattr(service, "deployDir", f"{controller.pwd}src/{service.name}/deploy/")
                service.dockerfile_path = getattr(service, "dockerfilePath", f"{service.root_dir}Dockerfile")
                service.k8s_service_name = getattr(service, "k8sServiceName", f"{controller.project.name}-{service.name}-service")
                service.k8s_deployment_name = getattr(service, "k8sDeploymentName", f"{controller.project.name}-{service.name}-deployment")
                services.append(service)

            return fn(controller, services, **_)

        return wrapper
    
    return inner

class Command:
    def __init__(self,):
        self.pwd = os.getcwd() + "/"
        self.config_path = f"{self.pwd}tapis-project.json"
        self.project = None