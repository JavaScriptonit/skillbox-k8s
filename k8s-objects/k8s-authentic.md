### Аутентификация и авторизация в кластере Kubernetes:
Каждый запрос перед попаданием в etcd проходит 3 стадии для определения пользователя и прав в кластере:
1. Аутентификация - кто мы?
2. Авторизация - что ты можешь делать?
3. Admission Control - могут изменить или отклонить запрос
    1. Admission Controller перехватывает запрос в k8s Api перед записью в etcd


# Аутентификация в k8s:
1. Когда сервер Api получает запрос - запрос проходит через список плагинов Аутентификации
    1. 1ый плагин, который может извлечь эту информацию из запроса - возваращает в ядро сервера Api имя пользователя, id и группы
    2. Сервер Api прекращает работы остальных плагинов и переходит ко 2ому этапу

# Типы клиентов в кластере:
1. Пользователи, которые работают через kubectl
2. Service account - единственный объект k8s, который похож на объект пользователей
    1. Нужен для авторизации пользователей внутри k8s

# Service account:
1. `kubectl get sa -n kube-system` - default sa
2. `kubectl get sa coredns -n kube-system`
    1. `kubectl get sa coredns -n kube-system -o json` - найти имя секрета, где SA хранит токен
3. `kubectl get po coredns-787d4945fb-gsv6g -n kube-system -o json` - get serviceAccount/serviceAccountName - coredns
4. `kubectl get secret coredns-token-g6gkz -n kube-system -o jsonpath='{.data.token}' | base64 -d` - получить раскодированный token из секрета
5. ### `kubectl config view | grep server` - адрес Api сервера: https://kubernetes.docker.internal:6443 / https://127.0.0.1:52935
6. `curl -k https://127.0.0.1:52935` - проверить доступ к Api серверу
    1. `curl -k https://127.0.0.1:52935 -H "Authorization: Bearer $(kubectl get secret coredns-token-g6gkz -n kube-system -o jsonpath='{.data.token}' | base64 -d)"` - курл с токеном для авторизации в Api сервере
    2. `curl -k https://127.0.0.1:52935/api/v1/services` - получить сервисы всего кластера
# Create Service account Pod:
7. `kubectl apply -f nginx-pod-sa.yaml` - create pod in -n kube-system with serviceAccountName: coredns
8. `kubectl exec -it nginx-pod -n kube-system -- bash` - bash created pod
    1. `cd /var/run/secrets/kubernetes.io/serviceaccount` - директория с токеном и ca.crt
    2. `cat token` - получить токен для проверки
    3. `https://jwt.io/` - decode token от coredns

# Плагины аутентификации:
Плагины активируются при помощи параметров командной строки при запуске сервера Api.

1. Пользовательские сертификаты - только для небольшого кол-ва пользователей, так как нельзя отозвать сертификаты
2. Файл с токенами - подложить файл к Api серверу со всеми пользователями, группами и токенами в обычный файл.txt
    1. Запускаем файл с параметром -tokenAuthFile
    2. Только для маленького кластера с небольшим кол-вом пользователей
    3. Если Api серверов несколько - файл нужно подкладывать для всех серверов и синхронизировать
        1. `docker exec -it minikube bash` - bash кластера
        2. `cd /var/lib/minikube/certs/` - сертификаты для Api сервера
        3. `vi static-tokens` - создать файл с пользователем для Api сервера
            1. `31ada4fd-adec-460c-809a-9e56ceb75269,user1,1234,developer` - value static-tokens
        4. ### `minikube start --extra-config=apiserver.token-auth-file=/var/lib/minikube/certs/static-tokens` - запустить кластер с конфигом для Api сервера
        5. `docker ps | grep api` - list Api containers
        5. `docker inspect 8d4b222258e4` - inspect api
            1. `"--token-auth-file=/var/lib/minikube/certs/static-tokens"`- in Entrypoint
        6. `kubectl cluster-info dump | less` - проверить конфигурацию кластера
            1. `/auth-file` - найти параметр
        7. `curl -k -H "Authorization: Bearer 31ada4fd-adec-460c-809a-9e56ceb75269" https://127.0.0.1:56994` - curl с токеном для Api сервера
            1. `curl -k -H "Authorization: Bearer 31ada4fd-adec-460c-809a-9e56ceb75269" https://127.0.0.1:54726/api/v1` - get APIResourceList
            2. `curl -k -H "Authorization: Bearer 31ada4fd-adec-460c-809a-9e56ceb75269" https://127.0.0.1:54726/api/v1/namespaces/default/pods` - get pods
            3. `curl -k -H "Authorization: Bearer 51ada4fd-adec-460c-809a-9e56ceb75269" https://127.0.0.1:57186/api/v1/namespaces/kube-system/pods` - get kube pods

3. Файл с пользователями/паролями - с версии 1.19 способ удалён
4. Service account - применим для внутренних пользователей. Аутентифицируемся по ключу, который генерирует k8s
5. Authenticating Proxy - рабочий способ для Prod решений. Api сервер конфигурируется чтобы аутентифицировать пользователей по кастомным заголовкам в запросе (xRemoteUser, xRemoteGroup). Хэдеры принимаются только от клиентов со спец сертом
6. OpenID Connect Provider - расширение протокола Oauth. Рабочий способ для Prod решений.
    1. Логинемся на стороннего провайдера
    2. Провайдер предоставляет Access token