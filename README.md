# Tapis Project Util [BETA]
A CLI tool to streamline development and deployment of Tapis services in local minikube and kubernetes envrionments.

## Installation
Clone the github repository to the directory of your choice and alias the `tapis-project-util.sh` file to the command of your choice. `t` is the preferred alias.

## Dependencies
The tapis project util requires `python3`, `docker`, `kubectl`, and `minikube`.
This dev util only makes use of the standard library in python3 and thus, does not require you to start use virtual environment.

### docker
[https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

### kubectl
[https://kubernetes.io/docs/tasks/tools/](https://kubernetes.io/docs/tasks/tools/)

### minikube
[https://minikube.sigs.k8s.io/docs/start/](https://minikube.sigs.k8s.io/docs/start/)

## List of commands
- `system_start`: starts minikube with the specified number of nodes - `t system_start [number of nodes]`
- `system_stop` stops all minikube control and worker nodes - `t system_stop`
- `dashboard` starts the minikube dashboard - `t dashboard`
- `up` runs the burnup script for the specified services - `t up api rabbitmq proxy`
- `down` runs the burndown script for the specified services - `t down api rabbitmq proxy`
- `build` builds an image from the services Dockerfile and tags with the with the label specified in the command. `t build [serviceName:tag]`
- `push` pushes the local image for the specified services to a remote repository `t push [serviceName:tag]`
- `buildp` runs the following commands for the services in the order provided. `build`, `push` - `t buildp [serviceName1:tag] [serviceName2:tag]`
- `rebuild` - runs the following commands for the services in the order provided. `down`, `build`, `push`, `up` `t rebuild [serviceName:tag]`
- `exec` Execs into the pod for a given service - `t exec [serviceName]`
- `watch` Follows the pod logs for a given service - `t watch [serviceName]`
- `expose`
- `exposed`

