# Create the helmchart. Создать /Users/aashabunov/IdeaProjects/kubernetes/webapp1 с шаблонами
```
helm create webapp1
```

# Follow along with the video
- Create the files per the video https://www.youtube.com/watch?v=jUYNS90nq8U, copying and pasting from templates-original
- you can also use the files in the solution folder

# Устанавливает чарт Helm под названием "webapp1" в кластер Kubernetes под именем "mywebapp-release".
# Чтобы удалить приложение, установленное с помощью команды helm install воспользоваться командой helm uninstall
```
helm install mywebapp-release webapp1/ --values webapp1/values.yaml
helm uninstall mywebapp-release
helm install myexporters-release myexporters/ --values myexporters/values.yaml
helm uninstall myexporters-release
```

# Upgrade after templating
```
helm upgrade mywebapp-release webapp1/ --values webapp1/values.yaml
helm upgrade --install myexporters-release /Users/aashabunov/IdeaProjects/kubernetes/myexporters
```

# Accessing it
Run service tunnel:
```
minikube service mywebapp --url
minikube service -n dev mywebapp --url
minikube service -n prod mywebapp --url
```
service output example: http://127.0.0.1:50268
```
ps -ef | grep docker@127.0.0.1
ps -ef | grep docker@127.0.0.1
1529087358 98047 98030   0  4:58   ttys010    0:00.02 ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o IdentitiesOnly=yes -N docker@127.0.0.1 -p 49368 -i /Users/aashabunov/.minikube/machines/minikube/id_rsa -L 60185:10.109.166.40:80
1529087358 14440 14423   0  5:38   ttys011    0:00.01 ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o IdentitiesOnly=yes -N docker@127.0.0.1 -p 49368 -i /Users/aashabunov/.minikube/machines/minikube/id_rsa -L 54026:10.99.73.145:80
1529087358 14647 14634   0  5:39   ttys012    0:00.01 ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o IdentitiesOnly=yes -N docker@127.0.0.1 -p 49368 -i /Users/aashabunov/.minikube/machines/minikube/id_rsa -L 54138:10.98.212.99:80
1529087358 15682 15490   0  5:41   ttys015    0:00.00 grep docker@127.0.0.1
```

# List all pods:
```
kubectl get pods --namespace=prod
kubectl get pods --namespace=dev
kubectl get pods --namespace=default
```
`kubectl get po -A` - pods all namespaces

# SSH minikube:
```
minikube ssh docker ps
```

# Turn off proxy minikube:
```
minikube config unset http_proxy
minikube config unset https_proxy
```

# Delete pods to restart containers:
```
kubectl delete pods --all
```

# Inspect Pod events and info:
```
kubectl describe pod mydeployment-6559fcc65f-26snb
```

# KUBECTL commands:
1. `kubectl --help` - commands list
2. `kubectl config` - Modify kubeconfig files - ${HOME}/.kube/config
    1. `kubectl config get-contexts`
    2. `kubectl config get-clusters`
    3. `kubectl config get-users`
3. `kubectl cluster-info` - Kubernetes control plane is running at https://127.0.0.1:55247
4. `kubectl get no -o wide` - wide nodes info
    1. `kubectl get nodes` - list nodes
    2. `kubectl get nodes --show-labels` - list of nodes with labels
    3. ### `kubectl get endpoints` - все ip:port кластера
        1. `kubectl describe endpoints nginx-deployment ` - посмотреть endpoint подробнее
5. `kubectl delete pods --all -n prod`
    `kubectl delete pods --all -n dev`
    `kubectl delete pods --all`
6. ### `kubectl config current-context` - check context
7. `kubectl config use-context docker-desktop` - change context
# Kubectl Labels:
8. `kubectl get po --show-labels` - list pods labels
9. `kubectl get po -l app=nginx ` - filter by label
    1. `kubectl get po -l app!=nginx,cluster=prod ` - not equal
    2. `kubectl delete po -l cluster=prod` - delete by cluster tag
10. `kubectl label node minikube env=dev` - tag Node
11. `kubectl label node minikube env=prod --overwrite` - change Node tag


# MINIKUBE commands:
1. `minikube image load server:1.0` - laod image from local to cluster
2. `minikube status` - cluster status


# Work in cluster:
1. `curl -v https://registry-1.docker.io/v2/` - check proxy
2. `sudo vi /etc/resolv.conf` - Установите правильные DNS-серверы в вашем окружении Minikube
3. Файл `/etc/systemd/system.conf.d/proxy-default-environment.conf` предназначен для настройки переменных окружения по умолчанию для всех служб и процессов, запускаемых в вашей системе с использованием systemd.
    `[Manager]`
    `DefaultEnvironment="HTTP_PROXY=http://prx-srv.mbrd.ru:3128" "HTTPS_PROXY=http://prx-srv.mbrd.ru:3128" "NO_PROXY=*.test.example.com,.example2.com,127.0.0.0/8,control-plane.minikube.internal"`
4. `sudo systemctl daemon-reload`
5. `sudo systemctl restart docker`