# Безопасность, Capabilities и Pod Security Policies

### Linux Capabilities (группы системных операций):
Делят root права на набор отдельных привелегий:
1. SETPCAP
2. SYS_ADMIN
3. SYS_NICE
4. SYS_TIME - группа с правами изменения системного времени
5. NET_ADMIN
6. NET_RAW

Пример:
1. `docker run --network=host nginx` - запуск контейнера с правами
2. `docker run --network=host --cap-drop CAP_NET_BIND_SERVICE nginx` - запуск контейнера без прав слушать на порту 80
    1. nginx: [emerg] bind() to 0.0.0.0:80 failed (13: Permission denied)

# Security Context:
Это настройки, которые определяют привилегии и доступы, которые будет иметь под и его контейнеры

# Create Pod with user:
1. `kubectl run nginx --image=nginx -n kube-system --as=user1` - Error from server (Forbidden): pods is forbidden: User "user1" cannot create resource "pods" in API group "" in the namespace "kube-system"
2. `kubectl run nginx --image=nginx -n default --as=user1` - создать под в доступном namespace

# Создать pod-hack для похищения config.yaml из кластера для безграничного доступа в кластере:
1. Для запуска под на мастер узле - нужно добавить метку minikube кластеру
    1. `kubectl label node minikube node-role.kubernetes.io/master=""`
    2. `kubectl get nodes` - проверить доступные узлы 
        1. minikube   Ready    control-plane,master   4d20h   v1.26.3
2. `kubectl exec -ti nginx-hack -n default -- bash` - зайти в shell пода
3. `cd /master/etc/kubernetes` - зайти в созданную директорию пода
4. `cat admin.conf` - показать созданный файл
    1. `vi config.yaml` - сохранить локально конфиг файл
5. `kubectl --kubeconfig=config.yaml auth can-i "*" "*"` - проверить доступ на все действия в кластере 
    1. Unable to connect to the server: dial tcp: lookup control-plane.minikube.internal: no such host - нужно поменять хост
    2. `kubectl config view` - server: https://127.0.0.1:62928 - поменять его в созданном локальном config.yaml
    3. `security-context % kubectl --kubeconfig=config.yaml auth can-i "*" "*" -n kube-system` - yes

# PodSecurityPolicy:
PSP - это механизм в Kubernetes, который позволяет администраторам кластера устанавливать политики безопасности для использования подами. PSP позволяет контролировать различные аспекты безопасности, такие как использование привилегий, доступ к хостовой файловой системе, использование пространства имен IPC и другие ограничения.

1. ### `minikube start --extra-config=apiserver.enable-admission-plugins=PodSecurityPolicy --addons=pod-security-policy` - enable PSP (включает использование PodSecurityPolicy)
    1. При запуске с параметром (когда PSP еще не созданы ранее) ВСЕ поды, которые не могут пройти проверки - запуститься не могут
    2. minikube создаст дефолтные разрешительные и запретительные политики и привяжет их
2. https://github.com/rancher/rke2/issues/4313 - "command failed" err="enable-admission-plugins plugin \"PodSecurityPolicy\" is unknown"
    1. `sudo journalctl -u docker` - errors docker
    2. `systemctl status kubelet` - errors kubelet
    3. `vi /etc/kubernetes/manifests/kube-apiserver.yaml` - check apiserver config
        1. `vi /Users/aashabunov/.minikube/machines/minikube/config.json` - minikube config
        2. `vi /Users/aashabunov/.minikube/profiles/minikube/config.json` - minikube config
    4. `sed -i "s/--enable-admission-plugins=PodSecurityPolicy//g" /etc/kubernetes/manifests/kube-apiserver.yaml && sudo systemctl restart kubelet` - delete arg in running minikube cluster
    5. 
