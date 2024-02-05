https://go.skillbox.ru/education/course/devops-kubernetes/1e0b6708-8a5b-4d77-9e72-cda8c15c497e/videolesson

# 9.1 Введение в мониторинг. Prometheus

1. Самые популярные программы для мониторинга k8s кластеров:
    1. Prometheus
        1. Prometheus-метрики состоят из ключа:значения, которые можно фильтровать по (ядру/ip/и тд), например, `cpu_usage`
        2. Prometheus не создан для хранения такой информации как текст.
        3. Prometheus - это БД (ключ:значение)
    2. Victoria-metrics

## Типы метрик:
1. Counter(счётчик) - значения, которые увелич. с теч. времени
2. Gauge(шкала) - значения, которые увелич. с теч. времени или уменьшатсья 
3. Histogram(гистограмма) - хранит инфо об изменении некоторого параметра в теч опред промежутка
4. Summary(сводка результатов) - расширенная гистограмма - непрерывное развитие во времени


## Prometheus-архитектура:
1. Prometheus-server:
    1. Retrieaval worker (отвечает за получение метрик и направление их в TSDB)
    2. TSDB (база данных для хранения горячих данных (метрик), default до 15 дней)
    3. HTTP server (API для получения сохр данных с TSDB)
2. Alertmanager (служить для отправки alert и уведомлений):
    1. Pagerduty
    2. Email
    3. etc
3. Pushgateway (Prometheus может забрать метрики из Pushgateway при выполнении jobs/cron jobs):
    1. Short-lived jobs
4. Service discovery (механизм, который позволяет автоматически обнаруживать и мониторить цели (targets) для сбора метрик)
    Это особенно полезно в динамических окружениях, где цели могут появляться и исчезать автоматически, таких как контейнерные оркестраторы (например, Kubernetes, Docker Swarm) или облачные окружения.
    1. k8s
    2. file_sd


## Установка:
1. Helm community chart
    1. https://artifacthub.io/packages/helm/prometheus-community/prometheus - Repository Info
    2. `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts` - добавить репо
    3. `kubectl create ns monitoring` - создать отдельный NS под мониторинг
    4. `helm upgrade --install prometheus prometheus-community/prometheus -n monitoring` - установить из него чарт
    5. `kubectl get po -n monitoring -w` - проверить работу подов
    6. `export POD_NAME=$(kubectl get pods -n monitoring -l "app=prometheus,component=server" -o jsonpath='{.items[0].metadata.name}')` - получить имя пода
    7. `kubectl port-forward -n monitoring $POD_NAME 9090` - forwarding from 127.0.0.1:9090 -> 9090
    8. `localhost:9090` - перейти в prometheus веб интерфейс локально
        1. alerts
        2. graph
        3. status
2. Prometheus operator:
    1. Создаёт в кластере k8s отдельный тип объект: service-monitor 

## Просмотр всех текущих целей Prometheus:

1. `localhost:9090/targets` - список всех целей
2. `kubectl describe service -n kube-system kube-dns` - посмотреть аннтоации сервиса для Prometheus



https://go.skillbox.ru/education/course/devops-kubernetes/00588d9d-421c-404c-86cb-d41dfb39bb73/videolesson

# 9.3 Prometheus exporters, Alert Manager и Grafana

1. `kubectl get deamonsets.apps -n monitoring` - проверка каждый ноды на наличие экспортёра осуществляется при помощи объекта `prometheus-node-exporter`
2. `kubectl get po -n monitoring` - `prometheus-node-exporter-pwlt`
    1. `kubectl describe po -n monitoring prometheus-node-exporter-pwlt` - достаёт все метрики с хоста
    2. `kubectl describe service -n monitoring prometheus-node-exporter` - чтобы прометеус начал собирать метрики с сервиса - должна быть аннотация
        1. `Annotations: prometheus.io/scrape: true`

## AlertManager.
Каналы доставки:

1. Email
2. Slack
3. PagerDuty
4. WebHooks
5. Другие

### Поменять ConfigMap Prometheus для создания правила нотификации:

1. `kubectl edit cm -n monitoring prometheus-server` - добавить строки из ./monitoring/9.3/alerting_rules.yaml в `data: alerting_rules.yml: | groups...`
2. `kubectl apply -f alert_manager.yaml -n monitoring` - создать конфигурацию для Slack (kind: ConfigMap) для нотификации в Slack по выбранному alert
    1. Пример конфигурации: `./monitoring/9.3/alert-manager.yaml` для отправки resolved notifications

## Grafana
https://artifacthub.io/packages/helm/grafana/grafana

1. `helm repo add grafana https://grafana.github.io/helm-charts` - добавить реп-ий
2. `helm repo update` - обновить все реп-ии
3. `helm install grafana grafana/grafana -n monitoring` - установить графану в ns monitoring
    1. Установщик подскажет как получить пароль от УЗ admin
    2. Установщик подскажет как прокинуть порт на localhost
4. Добавить prometheus как источник данных:
    1. localhost:3000 -> admin:password
    2. `kubectl get service -n monitoring` -> prometheus-server
    3. Configuration -> Data sorces -> add data source -> prometheus -> HTTP [URL: http://prometheus-server] -> save
5. Create dashboard -> Add a new panel -> promQL запрос (prometheus_http_requests_total)

