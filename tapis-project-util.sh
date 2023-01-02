#!/bin/bash

# Must have kubectl
if ! command -v kubectl &> /dev/null
then
    echo "kubectl is required"
    exit
fi

# Requires minikube
if ! command -v minikube &> /dev/null
then
    echo "minikube is required"
    exit
fi

# Requires minikube
if ! command -v python3 &> /dev/null
then
    echo "python3 is required"
    exit
fi


here=$(dirname $0)
python3 $here/main.py ${@}