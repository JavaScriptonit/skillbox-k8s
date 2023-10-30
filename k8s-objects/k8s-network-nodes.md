# Взаимодействие подов разных нод:
2 ВМ - сетевые адреса:
1. 172.16.100.1
2. 172.16.100.2
4 пода в 24 сети:
1. 10.10.10.1
2. 10.10.10.2
3. 10.10.11.1
4. 10.10.11.2
1 Роутер

# Сетевой пакет из пода 1 (10.10.10.1) в под 3 (10.10.11.1):
* ARP запрос (Address Resolution Protocol request) - это процесс получения MAC-адреса устройства по его IP-адресу в локальной сети. Когда устройство хочет отправить пакет на определенный IP-адрес, оно отправляет ARP запрос в сеть, чтобы узнать, какой MAC-адрес устройства с таким IP-адресом. Это необходимо, потому что передача данных в локальной сети происходит на физическом уровне по MAC-адресам, а не по IP-адресам.

1. Через [eth0] пакет покидает сетевой NS пода 1 ->
2. Попадает в root NS через [vethxxx] ->
3. Попадает в сетевой мост [bridge] ->
4. Делает ARP запрос* в поисках точки назначения ->
5. Из моста пакет переходит в сетевой интерфейс хоста [eth0], так ни у кого на сервере нет IP адреса соответствующего поду 3 ->
6. Попадает в маршрутизатор ->
    1. Routing настроен так что каждый пакет идущий на 10.10.11.1 -> надо отправлять на интерфейс 172.16.100.2 (2ой сервер)
7. Пакет попадает на сетевой интерфейс сервера 2 и перенаправляется в сетевой мост ->
8. Сетевой мост делает ARP запрос* и выясняет что ip принадлежит [vethyyy] ->
9. Пакет проходит через виртуальный линк и попадает в под 3


# Container Network Interface (CNI):
Стандарт для конфигурирования сети для k8s (Спецификация)
Ранее существовал CNM - Container Network Model от Docker для Docker Swarm
В спецификации определено что плагин должен иметь определенные методы:
1. ADD - вызывается при создании пода на хосте. При его вызове плагин должен создать новый виртуальный интерфейс [veth] между NS пода и root NS хоста
2. DEL - 
3. CHECK
4. VERSION

# Плагины:
1. Flannel - 1 из старейших плагинов
2. Calico - навороченный опенсорс проект (продвинутые фу-ии сетевой безопасности)
3. Weave Net
4. Cilium - позволяет делать шифрование трафика; Сложен в настройке

# Start minikube with Flannel plagin:
1. `minikube start --nodes 3 --cni flannel` - start cluster
2. `kubectl get ds -A` - list daemonsets
3. `kubectl get pods -A -o wide | grep flannel` - list flannel pods
4. ### `kubectl rollout restart ds kube-flannel-ds -n kube-flannel` - RESTART DS
5. `minikube node list` - nodes list:
```
minikube	192.168.67.2
minikube-m02	192.168.67.3
minikube-m03	192.168.67.4
```
6. `kubectl get nodes` - nodes list:
```
NAME           STATUS   ROLES           AGE   VERSION
minikube       Ready    control-plane   36s   v1.26.3
minikube-m02   Ready    <none>          18s   v1.26.3
minikube-m03   Ready    <none>          1s    v1.26.3
```
7. `kubectl describe configmaps kube-flannel-cfg -n kube-flannel` - kube-flannel configmap info
```
net-conf.json:
----
{
  "Network": "10.244.0.0/16",
  "Backend": {
    "Type": "vxlan"
  }
}
```
8. `docker exec -it minikube-m02 bash`, `root@minikube-m02:/# ip a` - посмотреть сетевые интерфейсы на worker ноде
```
5: flannel.1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1450 qdisc noqueue state UNKNOWN group default 
    link/ether ca:55:df:00:ee:8d brd ff:ff:ff:ff:ff:ff
    inet 10.244.1.0/32 scope global flannel.1
       valid_lft forever preferred_lft forever
```
9. `root@minikube-m02:/# ip -details link show flannel.1` - проверить созданное flannel виртуальное vxlan устройство - vxlan id 1 local 192.168.67.3 
```
5: flannel.1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1450 qdisc noqueue state UNKNOWN mode DEFAULT group default 
    link/ether ca:55:df:00:ee:8d brd ff:ff:ff:ff:ff:ff promiscuity 0 minmtu 68 maxmtu 65535 
    vxlan id 1 local 192.168.67.3 dev eth0 srcport 0 0 dstport 8472 nolearning ttl auto ageing 300 udpcsum noudp6zerocsumtx noudp6zerocsumrx addrgenmode eui64 numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535
```

# NetworkPolicy:
### Для контроля сетевого взаимодействия используются Сетевые политики:
Без сетевых политик - любой под имеет доступ к подам других нод в любых NS

1. `minikube start --cni calico` - создать кластер с CNI calico (который поддерживает сетевые политики)
2. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/network-policy/deny-all.yaml` - networking.k8s.io/default-deny created.
    1. `kubectl run app --image nicolaka/netshoot --labels="app=app" -- /bin/bash -c "sleep 3600"` - pod/app created
    2. `kubectl run db --image postgres --labels="app=database" --env="POSTGRES_PASSWORD=123"` - pod/db created
    3. `kubectl get po -o wide` - pods info
    4. `kubectl exec -it app -- bash` - connect pod app
    5. `telnet db <ip> 543` - check connection (timeout)
3. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/network-policy/allow.yaml` - networking.k8s.io/postgres-allow created.
    1. `kubectl exec -it app -- bash` - connect pod app
    2. `telnet db <ip> 543` - check connection (connected to <ip>)

