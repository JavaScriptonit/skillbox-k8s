# Create Namespace:
```
kubectl create namespace dev
kubectl create namespace prod
helm install mywebapp-release-dev webapp1/ --values webapp1/values.yaml -f webapp1/values-dev.yaml -n dev
helm install mywebapp-release-prod webapp1/ --values webapp1/values.yaml -f webapp1/values-prod.yaml -n prod
helm ls --all-namespaces
```

# Create Pod:
Поды эфимерны - могут появляться и исчезать в любое время. 
Нельзя знать ip адреса подов заранее. K8s даёт IP поду после его создания на ноде.
Может работать несколько реплик 1го приложения. Каждая реплика имеет свой IP.
Все поды должны быть доступны через 1 единый IP. 

1. `kubectl apply -f nginx.yaml` - create pod
    1. `kubectl apply -f server-app.yaml`
2. `kubectl logs nginx-pod` - logs of a pod
    1. `kubectl logs -f server-app` - в режиме онлайн
    2. `kubectl logs -f server-app -c server` - логи сервера
    3. `kubectl logs -f server-app -c client` - логи клиента
3. `kubectl get pod redis -n default -o jsonpath=”{..image}”` - посмотреть версию образа
    1. `kubectl get pod/nginx-deployment-7d6785dbdc-5fxtv -o jsonpath=”{..image}” ` - версия образа nginx
    2. ### `kubectl get po -o wide` - get pod's IP
4. `kubectl run redis --image=redis:5.0 -n default` - запуск redis pod
5. `kubectl edit pod redis -n default` - редактирование redis-pod.yaml
6. `kubectl edit pod nginx-f57dn` - edit pod
7. `kubectl run tmp-pod --rm -i --tty --image nicolaka/netshoot -- /bin/bash` - создать под, который будет удален после выхода из него
    1. `curl http://nginx-deployment` - test connection from tmp pod


# Create ReplicaSet (ReplicationController - old version):
Гарантирует, что указанное количество подов ReplicaSet всегда будет запущено и работать в кластере

1. `create -f rs_nginx.yaml` - create RS
2. `kubectl get rs` - list of rs
    1. `nginx-deployment-74888999bf` - 74888999bf - это хэш значения шаблона пода в описание deployment
    2. Хэш шаблона (74888999bf) помогает использовать 1 RS
3. `kubectl get po -o=custom-columns=NAME:.metadata.name,DATA:metadata.ownerReferences` - list pods by owner
4. `kubectl scale rs nginx --replicas=5` - scale replicas
5. `kubectl delete rs nginx` - delete rs and pods
6. selector: app может быть любым из перечисленных значений, например, nginx, web, frontend и т.д
```
    matchExpressions:
    - key: app
      operator: In
      values:
      - nginx
      - web
      - frontend
```
7. selector: все метки в селекторе точно соответствуют меткам в шаблоне пода
```
    matchLabels:
      app: nginx
```
8. `kubectl delete rs nginx --cascade=false` - delete rs and save pods

# Create Deployment:
1. `kubectl apply -f nginx-deployment.yaml` - create deploy and create RS and pods
2. `kubectl apply -f nginx-deployment.yaml --record=true` - тэгнуть деплой для возможности отката до его версии в будущем
3. `kubectl rollout status deployment nginx-deployment` - развертывание (deployment) с именем "nginx-deployment" успешно завершено
    1. `kubectl rollout status deployment test-app-deployment`
4. `kubectl delete deployment nginx-deployment` - delete deploy
# Стратегии Деплоя:
1. `RollingUpdate` - удаляет старые модули и одновременно создаёт новые
    1. `maxSurge` - 25% - насколько можно превысить кол-во реплик подов указанных в deploy
    2. `maxUnavailable` - 25% - сколько подов может быть недоступно
2. `Recreate` - удаляет старые перед созданием новых
3. `kubectl set image deployment test-app-deployment test-app=test-app:v2.0 --record` - задеплоить новую версию образа в деплой
4. `kubectl rollout undo deployment test-app-deployment` - откатить последний деплой
    1. `kubectl rollout undo deployment test-app-deployment --to-revision=2` - откатить к версии=2
5. `kubectl rollout history deployment test-app-deployment` - история деплоев


# Create DaemonSet:
В отличие от ReplicaSet, который обеспечивает желаемое количество подов в общем для всего кластера, DaemonSet гарантирует наличие одного экземпляра пода на каждом хосте. DaemonSet особенно полезен для запуска определенного набора подов, таких как лог-агенты, мониторинговые агенты и другие, на каждом узле кластера.

1. `Daemon в Linux` - это фоновая программа (не требующая взаимодействия с пользовтелем)
    Например:
    1. `Daemon Fluent Bit` - демон по сбору логов
    2. `Daemon Collectd` - демон мониторинга ноды
2. `DaemonSet` - обеспечивает запуск pods на каждой Node
3. `kubectl apply -f ../fluentd-ds.yaml` - create ds
4. `kubectl get ds` - list of ds
5. `kubectl delete -f ../fluentd-ds.yaml` - delete ds


# Create Service:
Сервис помогает pods взаимодействовать и находить друг друга внутри кластера.
Сервис даёт 1 единую и постоянную точку входа в группу подов.
Каждый сервис имеет свой IP и порт (которые не поменяются пока он существует).
Клиент подключается к Сервису и подключение маршрутизируется в 1 из подов.

1. `kubectl get services` - список сервисов
2. `kubectl describe service/nginx-deployment` - информация о сервисе
3. `kubectl expose deployment nginx-deployment --port 80 --target-port 80` - маршрутизация трафика с порта сервиса 80 на порты подов 80
    1. `kubectl get services` - после expose deployment port для просмотра сервиса
4. `kubectl create service clusterip mydb --tcp=5432:5432` - clusterip - тип сервиса


# Create Jobs:
Jobs используется для запуска однократных заданий в кластере. Когда задание Job успешно выполнено, Kubernetes завершает задание и сохраняет его историю выполнения.

1. `apply -f test-job.yaml` - create jobs
2. `kubectl get jobs` - list jobs
3. `kubectl logs pod/pi-5r94h` - logs after completing
# Create CronJobs:
Используется для запуска периодических заданий на основе расписания.
Поды CronJob автоматически удаляются после успешного выполнения задания, если в спецификации CronJob не указано сохранение истории выполнения.

1. `kubectl apply -f test-cronjob.yaml` - create CronJob
2. `kubectl get cronjob` - list of cronjobs

# Init Containers:
Использовать для инициализации подов. 
Используется для запуска контейнеров, которые должны быть выполнены перед основными контейнерами в поде

1. `kubectl apply -f test-init-pod.yaml` - create pod/busybox-pod 0/1 Init:0/1
2. `kubectl logs pod/busybox-pod -c init-db` - logs init container
3. `kubectl get event --field-selector involvedObject.name=busybox-pod` - filter logs
    1. `kubectl get event --field-selector involvedObject.name=busybox-pod --watch` - realtime logs