# Сетевая подсистема k8s
1. Контейнеры внутри пода имеют 1 общий уникальный IP-адрес
2. Поды могут общаться с любыми др подами, используя их IP-адреса без NAT
3. IP, который видит контейнер, должен быть таким для всех

`ip netns add ns-1` - 
`pause` - служебный контейнер, который является родительским контейнером для всех контейнеров пода
        - держит NS пода

Сетевые пары veth - Сетевое взаимодействие между 2ух NS через root NS
        - Pod 1 NS [eth0] -> [Сетевой NS root [eth0] [vethxxx] -> [bridge] -> [vethyyy]] -> Pod 2 NS [eth0]


# Запуск minikube с новым сетевым мостом вместо Docker моста
1. `minikube start --cni=bridge`
2. `kubectl run nginx --image=nginx` - создать под с nginx
3. `docker ps | grep -v kube` - показать созданные контейнеры с nginx и pause контейнером
```
CONTAINER ID   IMAGE                       COMMAND                  CREATED              STATUS              PORTS     NAMES
b04edc366242   nginx                       "/docker-entrypoint.…"   20 seconds ago       Up 19 seconds                 k8s_nginx_nginx_default_38b329f5-77eb-4754-b508-be5bcd28b995_0
16cb70bd9ca2   registry.k8s.io/pause:3.9   "/pause"                 22 seconds ago       Up 22 seconds                 k8s_POD_nginx_default_38b329f5-77eb-4754-b508-be5bcd28b995_0
```
4. `docker exec -it b04edc366242 bash` - подключиться с созданному контейнеру nginx для проверки сетевых интерфейсов
5. `ip a` - проверка сетевых интерфейсов
6. `apt update && apt install iproute2 iputils-ping` - скачать утилиты ip & ping
7. `root@nginx:/# ip a`:
```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
2: tunl0@NONE: <NOARP> mtu 1480 qdisc noop state DOWN group default qlen 1000
    link/ipip 0.0.0.0 brd 0.0.0.0
3: ip6tnl0@NONE: <NOARP> mtu 1452 qdisc noop state DOWN group default qlen 1000
    link/tunnel6 :: brd :: permaddr 92ac:c4d4:5d9e::
4: eth0@if18: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether aa:1f:f2:51:aa:38 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 10.244.2.209/16 brd 10.244.255.255 scope global eth0
       valid_lft forever preferred_lft forever
```
`LOOPBACK` - сетевой интерфейс
`eth0` - сетевой интерфейс с адресом 10.244.2.209 - один из концов вирт интерфейса `veth`
8. `root@minikube:/# ip a`:
```
5: bridge: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 8a:5f:a5:fa:ae:f9 brd ff:ff:ff:ff:ff:ff
    inet 10.244.0.1/16 brd 10.244.255.255 scope global bridge
       valid_lft forever preferred_lft forever
14: veth3202be53@if4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master bridge state UP group default 
    link/ether 82:68:5d:9c:a3:4a brd ff:ff:ff:ff:ff:ff link-netnsid 2
15: veth99b103d6@if4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master bridge state UP group default 
    link/ether 22:ea:c9:65:c7:b2 brd ff:ff:ff:ff:ff:ff link-netnsid 3
17: veth2141e09f@if4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master bridge state UP group default 
    link/ether c2:30:bb:a7:de:da brd ff:ff:ff:ff:ff:ff link-netnsid 4
18: veth370ddc67@if4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master bridge state UP group default 
    link/ether c2:0c:37:11:85:a8 brd ff:ff:ff:ff:ff:ff link-netnsid 1
```
9. `docker exec -it b04edc366242 bash`, `root@nginx:/# cat sys/class/net/eth0/iflink` - ответ 18 - это идентификатор интерфейса eth0 в контейнере. 
Идентификатор интерфейса (iflink) - это число, которое идентифицирует сетевой интерфейс в системе. Каждый интерфейс в системе имеет свой уникальный идентификатор. В данном случае, "18" указывает на идентификатор интерфейса eth0 в контейнере Nginx.
10. `root@minikube:/# grep -l 18 /sys/class/net/veth*/ifindex` - ответ /sys/class/net/veth370ddc67/ifindex - это 1 из 4 veth в ip a в кластере. Это 2ой конец в veth интерфейсе


# Сетевое взаимодействие мемжду подами:
1. `kubectl run nginx2 --image=nginx` и `kubectl run nginx --image=nginx` - запуск 2ух подов с nginx
2. `sudo apt update && sudo apt install tcpdump` - установить в кластер утилиту tcpdump для проверки трафика
3. `kubectl get pods -o wide` - IP подов:
```
NAME     READY   STATUS    RESTARTS   AGE   IP             NODE       NOMINATED NODE   READINESS GATES
nginx    1/1     Running   0          80m   10.244.2.209   minikube   <none>           <none>
nginx2   1/1     Running   0          14m   10.244.2.210   minikube   <none>           <none>
```
4. `sudo tcpdump -i bridge src 10.244.2.209` - посмотреть сетевой трафик по bridge мосту
5. `root@nginx:/# ping 10.244.2.210` - запустить трафик по сетевому мосту bridge из 1го контейнера пода в другой в рамках 1ой ноды