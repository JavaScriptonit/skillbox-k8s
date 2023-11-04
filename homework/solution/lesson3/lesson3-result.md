# Решение Задач урока №3 (5.5 Практическая работа)
## Задание №1:
https://go.skillbox.ru/education/course/devops-kubernetes/a757f195-0136-4c1e-902b-0903240959ac/homework

### Сборка образа и запуск приложения:
1. `docker build -t billing:v1.0 --build-arg http_proxy= --build-arg https_proxy= .` - создать образ без прокси
    1. `/Users/aashabunov/IdeaProjects/kubernetes/homework/devops-kubernetes-master/module-5/Homework/billing/app` - приложение
2. `minikube image load billing:v1.0` - добавить образ в кластер
3. `kubectl create -f db.yaml`, `kubectl create -f db.yaml` - создать 2 deployment с БД и приложением billing 
    1. `/Users/aashabunov/IdeaProjects/kubernetes/homework/devops-kubernetes-master/module-5/Homework/billing` - манифесты

### Проверка работоспособности приложения:
4. `kubectl run tmp-pod --rm -i --tty --image nicolaka/netshoot -- /bin/bash` - создать временный под для проверки запросов
5. `curl -X POST http://billing:8080/add?client_id=1\&amount=1000` - создать новую транзакцию
    1. `Transactioncurl http://billing:8080/get/1` - вывод
6. `curl http://billing:8080/get/1` - запросить детальную информацию по созданной транзакции
    1. `{"amount":1000,"client_id":"1","id":1}` - вывод
    


1. `telnet <INTERNAL-IP> 30007` - проверка сервиса типа NodePort с базой наружу на порту 30007
    1. `telnet 192.168.58.4:30007`
    2. `curl -v 192.168.58.4:30007`
2. `kubectl get po -o wide -n default`
3. `kubectl get all -o wide -n default`
4. `kubectl get nodes -o wide`
5. `kubectl describe service/postgres`:
    1. `10.244.2.9:5432` - pod ip
    2. `10.99.149.246:5432` - service ip
    3. `192.168.58.4:30007` - node ip
6. `kubectl get service postgres -o jsonpath='{.spec.ports[0].nodePort}'` - 30007 port сервиса
7. `kubectl exec -it postgres-75b55669c6-grfv2 -- psql -U user -d db` - подключиться к бд (проверить что БД внутри пода работает должным образом и принимает соединения)



## Задание №2:
1. `kubectl scale --replicas=0 deployment/billing` - скалирование реплик до 0
2. `kubectl create -f deny_all.yaml` - создать запретительную политику для ns
3. `kubectl scale --replicas=1 deployment/billing`
4. `kubectl exec -ti deployments/billing  -- bash` - создать NetworkPolicy чтобы разрешить сетевое взаимодействие billing → postgres:
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: 
  name: postgres-allow
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: database
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: app
    pods:
    - port: 5432
```
6. `apt update && apt install -y curl` -  установить курл чтобы проверить сетевой доступ до пода
7. `curl http://127.0.0.1:8080/getall`