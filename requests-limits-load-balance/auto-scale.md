https://go.skillbox.ru/education/course/devops-kubernetes/9890e5bc-5c4a-4141-b40d-d2a797088256/videolesson

# 8.3 Введение в автомасштабирование. Metrics-server и PDB:

## Автоматическое масштабирование:

1. Горизонтальное масштабирование подов и нод кластера изменяя их кол-во
или
Изменять запрашиваемые контейнерами пода ресурсы

    1. Что масштабировать? 
        В контексте k8s кластера:
        1. Node'ы
        2. Pod'ы
        3. Запросы ресурсов
    2. Когда масштабировать? 
        1. Metrics server собирает метрики с kubelet'ов, хранит их в ОП и никуда не складывает.
        2. Для мониторинга данных используется Prometheus, так как он хранит данные
        3. Ранее использовался hipster, который хранил полученные метрики во внешнем хранилище (influxdb)
    3. Как масштабировать?
        Пример нового API:
        ```
        apiVersion: apiregistration.k8s.io/v1
        kind: APIService
        metadata:
            labels:
                k8s-app: metrics-server
            name: v1beta1.metrics.k8s.io
        spec:
            group: metrics.k8s.io
            service:
                name: metrics-server # APIService с именем v1beta1.metrics.k8s.io указывает на сервис metrics-server в пространстве имен kube-system
                namespace: kube-system
            version: v1beta1
        ```
2. `minikube addons enable metrics-server` - включить аддон metrics-server в миникубе
или
`wget https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml` - скачать готовые манифесты
    1. `vi components.yaml` - ServiceAccount, ClusterRole (rbac), ClusterRoleBinding, Service, Deployment, APIService

3. `kubectl top nodes`, `kubectl top pods` - realtime metrics

4. `kubectl proxy --port=8080 &` - проксировать API к себе на локальную машину
    1. `curl -s http://localhost:8080/apis | grep metrics` - метрики будут доступны только после включения metrics-server

5. `kubectl apply -f ./components.yaml` - создать metrics-server

6. `kubectl proxy --port=8080 &`, `curl -s http://localhost:8080/apis/metrics.k8s.io/v1beta1/nodes/minikube-m02` - CPU & memory

7. `kubectl proxy --port=8080 &`, `curl -s http://localhost:8080/apis/metrics.k8s.io/v1beta1/pods/`- CPU & memory


## Pod Distruption Budget:
Подобъект PodDisruptionBudget (PDB) используется для управления доступностью подов в Kubernetes во время процедур обслуживания, таких как обновление версий, перезагрузка или удаление. PDB позволяет ограничить количество подов, которые могут быть одновременно недоступны в результате этих процедур.

#### Пример манифеста:
PDB устанавливает min кол-во доступных подов для подуровня с меткой app: server в 2. 
k8s будет поддерживать не менее двух доступных подов с меткой app: server, чтобы обеспечить непрерывность работы приложения:
```
apiVersion: policy/v1
kind: PodDistruptionBudget
metadata:
    name: server-pdb
spec:
    minAvailable: 2
    selector:
        matchLabels:
            app: server
```

1. `kubectl apply deployment nginx --image=nginx --replicas 4` - создать deployment

2. `kubectl get po -o -wide -w` - отображение подов

3. `kubectl drain minikube-m02 --ignore-daemonsets` - завершить работу всех подов nginx на minikube-m02 и одновременно создать реплики на 1ой ноде minikube

4. `kubectl apply pdb pdbdemo --min-available 2 -- selector "app=nginx"`

5. `kubectl delete deployment.apps nginx`

6. `kubectl uncordon minikube-m02` - сделать снова рабочей ноду minikube-m02

7. `kubectl apply deployment nginx --image=nginx --replicas 4` - пересоздать deployment, `kubectl drain minikube-m02 --ignore-daemonsets` - с pdb не будут сразу удалены все реплики, пока не будут созданы 2 новые реплики на другой ноде