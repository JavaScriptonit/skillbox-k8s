# Ingress:
1. `minikube addons enable ingress` - The 'ingress' addon is enabled
2. `kubectl run nginx --image nginx --labels="app=app"` - pod/nginx created
3. `kubectl expose pod nginx --port 80 --target-port 80` - service/nginx exposed
4. `kubectl get pods -o wide`:
```
NAME    READY   STATUS    RESTARTS   AGE     IP           NODE           NOMINATED NODE   READINESS GATES
nginx   1/1     Running   0          3m55s   10.244.2.5   minikube-m03   <none>           <none>
```
5. `kubectl describe service nginx`:
```
Name:              nginx
Namespace:         default
Labels:            app=app
Annotations:       <none>
Selector:          app=app
Type:              ClusterIP
IP Family Policy:  SingleStack
IP Families:       IPv4
IP:                10.107.55.202
IPs:               10.107.55.202
Port:              <unset>  80/TCP
TargetPort:        80/TCP
Endpoints:         10.244.2.5:80
Session Affinity:  None
Events:            <none>
```
6. `kubectl apply -f ingress/ing.yaml` - ingress.networking.k8s.io/my-app created
7. `kubectl describe ingress my-app`:
```
Address:          192.168.58.2
Rules:
  Host        Path  Backends
  ----        ----  --------
  *           
              /   nginx:80 (10.244.2.5:80)
Annotations:  nginx.ingress.kubernetes.io/rewrite-target: /
```
8. `kubectl run apache --image httpd --labels="app=app-apache"` - pod/apache created
9. `kubectl expose pod apache --port 80 --target-port 80` - service/apache exposed
10. `kubectl describe svc apache`:
```
TargetPort:        80/TCP
Endpoints:         10.244.2.8:80
```
11. `kubectl edit ingress my-app` - add apache:
```
  - http:
      paths:
      - backend:
          service:
            name: apache
            port:
              number: 80
        path: /apache
        pathType: Prefix
```
12. `kubectl describe ingress my-app`:
```
Rules:
  Host        Path  Backends
  ----        ----  --------
  *           
              /   nginx:80 (10.244.2.7:80)
  *           
              /apache   apache:80 (10.244.2.8:80)
Annotations:  nginx.ingress.kubernetes.io/rewrite-target: /
```


# Debug Ingress:
1. `curl -v http://192.168.58.2` - проверить доступ через ingress
    1. Failed to connect to 192.168.58.2 port 80 after 17 ms: Connection refused
2. `kubectl get pods -n ingress-nginx`:
```
NAME                                        READY   STATUS      RESTARTS   AGE
ingress-nginx-admission-create-fqw4t        0/1     Completed   0          34m
ingress-nginx-admission-patch-vjcpl         0/1     Completed   1          34m
ingress-nginx-controller-6cc5ccb977-hnxh2   1/1     Running     0          34m
```
3. `kubectl get po -n default` - проверить запущенный под с nginx
4. `kubectl logs pod/ingress-nginx-controller-6cc5ccb977-hnxh2 -n ingress-nginx` - логи контроллера
5. `ubectl get svc -n default`:
```
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1       <none>        443/TCP   4d1h
my-service   ClusterIP   10.109.214.77   <none>        80/TCP    18h
nginx        ClusterIP   10.107.55.202   <none>        80/TCP    30m
```
6. `minikube service list`:
```
|----------------------|------------------------------------|--------------|-----|
|      NAMESPACE       |                NAME                | TARGET PORT  | URL |
|----------------------|------------------------------------|--------------|-----|
| default              | kubernetes                         | No node port |     |
| default              | my-service                         | No node port |     |
| default              | nginx                              | No node port |     |
| ingress-nginx        | ingress-nginx-controller           | http/80      |     |
|                      |                                    | https/443    |     |
| ingress-nginx        | ingress-nginx-controller-admission | No node port |     |
| kube-system          | kube-dns                           | No node port |     |
| kubernetes-dashboard | dashboard-metrics-scraper          | No node port |     |
| kubernetes-dashboard | kubernetes-dashboard               | No node port |     |
|----------------------|------------------------------------|--------------|-----|
```
7. `kubectl delete -f svc.yaml` - service "my-service" deleted


# Объекты Ingress:
```
kubectl get all -n ingress-nginx
NAME                                            READY   STATUS      RESTARTS   AGE
pod/ingress-nginx-admission-create-fqw4t        0/1     Completed   0          4h14m
pod/ingress-nginx-admission-patch-vjcpl         0/1     Completed   1          4h14m
pod/ingress-nginx-controller-6cc5ccb977-hnxh2   1/1     Running     0          4h14m

NAME                                         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
service/ingress-nginx-controller             NodePort    10.98.65.225   <none>        80:30428/TCP,443:31998/TCP   4h14m
service/ingress-nginx-controller-admission   ClusterIP   10.97.31.183   <none>        443/TCP                      4h14m

NAME                                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ingress-nginx-controller   1/1     1            1           4h14m

NAME                                                  DESIRED   CURRENT   READY   AGE
replicaset.apps/ingress-nginx-controller-6cc5ccb977   1         1         1       4h14m

NAME                                       COMPLETIONS   DURATION   AGE
job.batch/ingress-nginx-admission-create   1/1           5m51s      4h14m
job.batch/ingress-nginx-admission-patch    1/1           5m52s      4h14m
```

`pod/ingress-nginx-admission-create-fqw4t и pod/ingress-nginx-admission-patch-vjcpl`: 
Это временные поды типа Job, которые выполнят необходимые операции для внедрения адмиссионного контроллера в кластер и патча (изменения) перечисленных подов.

`pod/ingress-nginx-controller-6cc5ccb977-hnxh2`: 
Это под, который содержит экземпляр контейнера с вашим ингресс-контроллером. Этот под отвечает за обработку входящих запросов и маршрутизацию их к соответствующим сервисам в кластере.

`service/ingress-nginx-controller`: 
Это служба, которая предоставляет сервис доступа к ингресс-контроллеру. Он определен как тип NodePort с открытыми портами 80 и 443 для обработки HTTP и HTTPS запросов. Ваш ингресс-контроллер будет доступен через IP-адрес узла кластера и один из указанных портов.

`service/ingress-nginx-controller-admission`: 
Это служба, которая предоставляет доступ к адмиссионному контроллеру для проверки и валидации конфигураций ингрессов. Эта служба используется внутренне в кластере и настроена для обработки только запросов на порт 443.

`deployment.apps/ingress-nginx-controller`: 
Это объект развертывания (deployment), который определяет, как создавать и управлять экземплярами вашего ингресс-контроллера. В этом случае, у вас есть один экземпляр ингресс-контроллера, запущенный в поде.
1. `kubectl get deployment.apps/ingress-nginx-controller -n ingress-nginx` - ingress-nginx-controller 1/1 1 1 4h31m
2. `kubectl exec -it deployment.apps/ingress-nginx-controller -n ingress-nginx -- bash`, `ps auxf | less` - процессы deployment:
```
PID   USER     TIME  COMMAND
    1 www-data  0:00 /usr/bin/dumb-init -- /nginx-ingress-controller --election-id=ingress-nginx-leader --controller-class=k8s.io/ingress-nginx --watch-ingress-wi
thout-class=true --configmap=ingress-nginx/ingress-nginx-controller --tcp-services-configmap=ingress-nginx/tcp-services --udp-services-configmap=ingress-nginx/udp
-services --validating-webhook=:8443 --validating-webhook-certificate=/usr/local/certificates/cert --validating-webhook-key=/usr/local/certificates/key
    7 www-data  0:26 /nginx-ingress-controller --election-id=ingress-nginx-leader --controller-class=k8s.io/ingress-nginx --watch-ingress-without-class=true --con
figmap=ingress-nginx/ingress-nginx-controller --tcp-services-configmap=ingress-nginx/tcp-services --udp-services-configmap=ingress-nginx/udp-services --validating
-webhook=:8443 --validating-webhook-certificate=/usr/local/certificates/cert --validating-webhook-key=/usr/local/certificates/key
   21 www-data  0:00 nginx: master process /usr/bin/nginx -c /etc/nginx/nginx.conf
  978 www-data  0:00 nginx: worker process
  979 www-data  0:00 nginx: worker process
  980 www-data  0:00 nginx: worker process
  981 www-data  0:00 nginx: worker process
  ```
 3. `cat /etc/nginx/nginx.conf | less`, `/apache`:
 ```
 location ~* "^/apache" {

                        set $namespace      "default";
                        set $ingress_name   "my-app";
                        set $service_name   "apache";
                        set $service_port   "80";
                        set $location_path  "/apache";
 ```
 4. `kubectl describe svc ingress-nginx-controller -n ingress-nginx`:
 ```
Port:                     http  80/TCP
TargetPort:               http/TCP
NodePort:                 http  30428/TCP
Endpoints:                10.244.0.12:80

Port:                     https  443/TCP
TargetPort:               https/TCP
NodePort:                 https  31998/TCP
Endpoints:                10.244.0.12:443
```

`replicaset.apps/ingress-nginx-controller-6cc5ccb977`: 
Это объект ReplicaSet, который обеспечивает поддержку запущенных экземпляров ингресс-контроллера. В данном случае, вы имеет одно экземплярное развитие, соответствующее одному экземпляру контроллера.

Разница между ingress-controller и объектами ingress:

`ingress-controller` - это компонент, который реализует механизм Ingress в вашем кластере Kubernetes. Он отвечает за маршрутизацию входящих запросов, включая балансировку нагрузки и выпуск сертификатов SSL/TLS.
Маршрутизацией и проксированием занимается ingress-controller. Он принимает входящие запросы и, основываясь на правилах, определенных в объекте ingress, маршрутизирует или проксирует трафик к соответствующим сервисам или подам в кластере Kubernetes

`ingress` - это объект, который определяет правила и настройки маршрутизации для веб-трафика в кластере. Ингресс содержит информацию о том, как поступать с входящими запросами, например, на какой сервис/под направлять запросы, как обрабатывать SSL/TLS и другие настройки.


# Ingress-контроллеры:

`Ingress от Kubernetes`: Это встроенный в Kubernetes механизм, который позволяет управлять входящим трафиком в кластере. Он позволяет определять правила маршрутизации на основе URL-путей или хостов и маршрутизировать трафик к соответствующим сервисам внутри кластера. Он не предоставляет никакого управления или настроек для балансировки нагрузки, SSL/TLS или других дополнительных функций.
Бесплатно. Встроенный механизм Kubernetes.

`Ingress от компании Nginx`: Этот контроллер использует Nginx для обработки запросов Ingress внутри кластера. Он предоставляет богатые возможности для маршрутизации трафика, балансировки нагрузки и управления SSL/TLS. Кнопка настройки логов и ведение статистики обращений. Он является одним из самых популярных контроллеров Ingress в сообществе Kubernetes.
Существуют две версии: бесплатная (Nginx Community Edition) и платная (Nginx Plus). Однако, для использования в качестве Ingress-контроллера в Kubernetes, вы можете использовать бесплатную версию.

`Traefik`: Это многофункциональный Ingress-контроллер, специально разработанный для облачных и контейнерных сред. Он автоматически обнаруживает новые сервисы и обновления конфигурации Ingress, обеспечивает балансировку нагрузки, маршрутизацию на основе правил и поддержку SSL/TLS. Он имеет интуитивно понятный интерфейс и возможность динамического конфигурирования через файлы YAML или API.
Бесплатно и с открытым исходным кодом. Можно использовать его в качестве бесплатного Ingress-контроллера.

`HAProxy`: Это популярный сервер прокси и диспетчер нагрузки с открытым исходным кодом. Он может использоваться в качестве Ingress-контроллера для маршрутизации трафика и балансировки нагрузки в контейнерной среде. HAProxy обладает мощными возможностями настройки и контроля, но требует дополнительной конфигурации и управления в сравнении с другими контроллерами.
Бесплатно и с открытым исходным кодом. Можно использовать его в качестве бесплатного Ingress-контроллера.

`Kong`: Это полнофункциональный API-шлюз с открытым исходным кодом и Ingress-контроллером для Kubernetes. Kong предоставляет управление общим доступом к API, аутентификацию, авторизацию, логирование и другие функции, связанные с управлением API. Он интегрируется с популярными базами данных и имеет мощные возможности по масштабированию и управлению трафиком API.
Существуют две версии: бесплатная (Kong Community Edition) и платная (Kong Enterprise). Бесплатная версия Kong Community Edition может быть использована как бесплатный Ingress-контроллер.
