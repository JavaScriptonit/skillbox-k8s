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
                name: metrics-server
                namespace: kube-system
            version: v1beta1
        ```
