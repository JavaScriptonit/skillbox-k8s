# Сервисы Deep Dive:

### Kube-Proxy:
Режим работы:
1. user space - маршрутизация трафика на ноде в поды - практически не используется такой режим
2. iptables - настраивает правила iptables на ноде и таким образом маршрутизирует трафик по подам
3. ipvs - ip virtual server - быстрая маршрутизация и балансировка трафика


# Example:
1. `minikube start --nodes 3 --cni flannel` - start cluster
2. `config % kubectl run nginx1 --image nginx --labels="app=my-app"` - pod/nginx1 created
3. `kubectl run nginx2 --image nginx --labels="app=my-app"` - pod/nginx2 created
4. `kubectl apply -f svc.yaml` - service/my-service created
5. `kubectl get po -o wide` - ip порты подов
6. `kubectl describe service/my-service` - Endpoints: 10.244.2.3:80,10.244.2.4:80 - эндпоинты подов
7. ### `docker exec -it minikube-m02 bash`, `root@minikube-m02:/# iptables -t nat -n --line-numbers -L KUBE-SERVICES`:
KUBE-SVC-FXIYY6OHUSNBITIX - default/my-service cluster IP */ tcp dpt:80
```
Chain KUBE-SERVICES (2 references)
num  target     prot opt source               destination         
1    KUBE-SVC-NPX46M4PTMTKRN6Y  tcp  --  0.0.0.0/0            10.96.0.1            /* default/kubernetes:https cluster IP */ tcp dpt:443
2    KUBE-SVC-TCOU7JCQXEZGVUNU  udp  --  0.0.0.0/0            10.96.0.10           /* kube-system/kube-dns:dns cluster IP */ udp dpt:53
3    KUBE-SVC-ERIFXISQEP7F7OF4  tcp  --  0.0.0.0/0            10.96.0.10           /* kube-system/kube-dns:dns-tcp cluster IP */ tcp dpt:53
4    KUBE-SVC-JD5MR3NA4I4DYORP  tcp  --  0.0.0.0/0            10.96.0.10           /* kube-system/kube-dns:metrics cluster IP */ tcp dpt:9153
5    KUBE-SVC-CEZPIJSAUFW5MYPQ  tcp  --  0.0.0.0/0            10.100.128.175       /* kubernetes-dashboard/kubernetes-dashboard cluster IP */ tcp dpt:80
6    KUBE-SVC-Z6GDYMWE5TV2NNJN  tcp  --  0.0.0.0/0            10.104.59.59         /* kubernetes-dashboard/dashboard-metrics-scraper cluster IP */ tcp dpt:8000
7    KUBE-SVC-FXIYY6OHUSNBITIX  tcp  --  0.0.0.0/0            10.109.214.77        /* default/my-service cluster IP */ tcp dpt:80
8    KUBE-NODEPORTS  all  --  0.0.0.0/0            0.0.0.0/0            /* kubernetes service nodeports; NOTE: this must be the last rule in this chain */ ADDRTYPE match dst-type LOCAL
```
8. `root@minikube-m02:/# iptables -t nat -n --line-numbers -L KUBE-SVC-FXIYY6OHUSNBITIX`:
KUBE-SEP - Service Endpoint
```
Chain KUBE-SVC-FXIYY6OHUSNBITIX (1 references)
num  target     prot opt source               destination         
1    KUBE-MARK-MASQ  tcp  -- !10.244.0.0/16        10.109.214.77        /* default/my-service cluster IP */ tcp dpt:80
2    KUBE-SEP-BVVT36TDQ4XITJXY  all  --  0.0.0.0/0            0.0.0.0/0            /* default/my-service -> 10.244.2.3:80 */ statistic mode random probability 0.50000000000
3    KUBE-SEP-BENFWTFL3RRJWBIC  all  --  0.0.0.0/0            0.0.0.0/0            /* default/my-service -> 10.244.2.4:80 */
```
9. `kubectl run nginx3 --image nginx --labels="app=my-app"` - создать еще 1 под для проверки маршрутизации
10. `docker exec -it minikube-m02 bash`, `iptables -t nat -n --line-numbers -L KUBE-SVC-FXIYY6OHUSNBITIX`:
```
Chain KUBE-SVC-FXIYY6OHUSNBITIX (1 references)
num  target     prot opt source               destination         
1    KUBE-MARK-MASQ  tcp  -- !10.244.0.0/16        10.109.214.77        /* default/my-service cluster IP */ tcp dpt:80
2    KUBE-SEP-WGKLWVVFG4NQGKEX  all  --  0.0.0.0/0            0.0.0.0/0            /* default/my-service -> 10.244.1.3:80 */ statistic mode random probability 0.33333333349
3    KUBE-SEP-BVVT36TDQ4XITJXY  all  --  0.0.0.0/0            0.0.0.0/0            /* default/my-service -> 10.244.2.3:80 */ statistic mode random probability 0.50000000000
4    KUBE-SEP-BENFWTFL3RRJWBIC  all  --  0.0.0.0/0            0.0.0.0/0            /* default/my-service -> 10.244.2.4:80 */
```
11. `root@minikube-m02:/# iptables -t nat -n --line-numbers -L KUBE-SEP-BENFWTFL3RRJWBIC`:
Трафик попадает в под
```
Chain KUBE-SEP-BENFWTFL3RRJWBIC (1 references)
num  target     prot opt source               destination         
1    KUBE-MARK-MASQ  all  --  10.244.2.4           0.0.0.0/0            /* default/my-service */
2    DNAT       tcp  --  0.0.0.0/0            0.0.0.0/0            /* default/my-service */ tcp to:10.244.2.4:80
```

# Способы опубликования СЕРВИСА наружу:
1. `kubectl proxy --port 8080` - публикация API
    1. `http://localhost:8080/api/v1` - кластер
    2. `http://localhost:8080/api/v1/namespaces/default/services/my-service/proxy/` - nginx
2. `kubectl port-forward service/my-service 10000:80` - 2ой вариант публикования
    1. `http://localhost:10000/` - nginx


# NodePort (Service Type):
1. `kubectl apply -f cni-flannel/np.yaml` - service/my-service-nodeport created
2. `docker exec -it minikube-m02 bash`, `apt update && apt install net-tools` - update packages on worker node
3. `netstat -ano | grep -i list` - check port:
Должен быть nodePort: 30007, к которому можно обратиться через ip ноды и порта - curl http://192.168.58.2:30007
```
tcp        0      0 127.0.0.11:35021        0.0.0.0:*               LISTEN      off (0.00/0/0)
tcp        0      0 127.0.0.1:10248         0.0.0.0:*               LISTEN      off (0.00/0/0)
tcp        0      0 192.168.58.3:10010      0.0.0.0:*               LISTEN      off (0.00/0/0)
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      off (0.00/0/0)
tcp6       0      0 :::40167                :::*                    LISTEN      off (0.00/0/0)
tcp6       0      0 :::2376                 :::*                    LISTEN      off (0.00/0/0)
tcp6       0      0 :::10249                :::*                    LISTEN      off (0.00/0/0)
tcp6       0      0 :::10250                :::*                    LISTEN      off (0.00/0/0)
tcp6       0      0 :::10256                :::*                    LISTEN      off (0.00/0/0)
tcp6       0      0 :::22                   :::*                    LISTEN      off (0.00/0/0)
```

# LoadBalancer:
1. `kubectl apply -f cni-flannel/lb.yaml ` - service/my-service-lb created
2. `kubectl get services` - будет доступен по адресу EXTERNAL-IP
```
NAME                  TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
my-service-lb         LoadBalancer   10.104.175.68    <pending>     80:31006/TCP   59s
```