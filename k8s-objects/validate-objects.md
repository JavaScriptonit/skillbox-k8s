# K8s Архитектура:

Master Node (Kubernetes control plane):
MN общается с WN через Api server
1. `Scheduler` - определяет расположение контейнеров на Node
2. `Api server` - Kube API - единственный пишет напрямую в базу etcd. REST/GRPC server для общения со всеми компонентами кластера
3. `Controller Manager` - компонент приводящий текущее состояние кластера к желаемому. CM - это группа сервисов (node controller, replication controller, endpoints controller, account controller, token controller)
4. `etcd` - хранилище данных (key:value) - состояние нашего кластера. Нужен backup. В prod мин 3 экз.

Worker Node:
1. `kubelet` - основной компонент на каждой Node. Управляет контейнерами на ноде. 
2. `kubeproxy` - отвечает за сетевое взаимодейтсвие между контейнерами (iptables правила)

1. `docker/containerd/CRI-O` - 

# Клиент:

1. Аутентификация в API server
2. Авторизация на API server
3. Admission Controller (Часть API сервера) выполняет действия после п.1, п.2 по распределению ресурсами
    Примеры (В minikbe работает по-умолчанию, в др. кластерах нужно включить их использование с параметром enableAdmissionPlugins с параметром API server):
    1. InitialResources - устанавливает ресурсы по умолчанию для ресурсов контейнера
    2. LimitRanger - устанавливает значения по умолчанию для запросов и лимитов контейнера
    3. ResourceQuota - считает кол-во объектов (pods/RS) и общие потребляемые ресурсы и предотвращает их превышение
    4. MutatingAdmissionWebhook - модифицирует
    5. ValidatingAdmissionWebhook - валидирует запрос

