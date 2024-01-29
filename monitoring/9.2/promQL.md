https://go.skillbox.ru/education/course/devops-kubernetes/ae44ee2c-e331-4be0-acfd-d46980c29b1f/videolesson

# 9.2 Prometheus. Service Discovery и PromQL

## Scrapping (сбор метрик с целей):

1. TSDB <-- Prometheus <-- Pod1[Target 1, localhost:8080/metrics]/Pod2[Target 2, localhost:9090/metrics]/Pod3[Target 3, localhost:8080/metrics] <-- cpu_usage 10.7, memory usage 156, disk_free 80, cpu_usage 10.7, memory usage 156, clients_connected 120, cpu_usage 10.7, memory usage 156, http_latency 101
2. `export POD_NAME=$(kubectl get pods -n monitoring -l "app=prometheus,component=server" -o jsonpath='{.items[0].metadata.name}')` - получить имя пода
3. `kubectl port-forward -n monitoring $POD_NAME 9090` - forwarding from 127.0.0.1:9090 -> 9090
4. `localhost:9090/metrics` - открыть все доступные метрики Prometheus


## PromQL:
Как достать метрики из самого Prometheus:

`http://localhost:9090/graph` - просмотр и анализ различных метрик и данных, собранных и хранящихся в Prometheus

### Примеры функций:

1. `irate / rate `
2. `sum`
3. `count`
4. `Арифметические операции`

Example: 
1. `promhttp_metrics_handler_requests_total{job="prometheus", code="200"}` - получить количество запросов с кодом ответа "200" для задания (job) "prometheus"
2. rate(`promhttp_metrics_handler_requests_total{job="prometheus", code="200"}`[10m]) - теперь можно увидеть метрику за интервал 10 минут на графике