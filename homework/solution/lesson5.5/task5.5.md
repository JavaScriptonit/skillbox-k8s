https://go.skillbox.ru/education/course/devops-kubernetes/a757f195-0136-4c1e-902b-0903240959ac/homework
https://gitlab.skillbox.ru/maksim_stepanov_3/devops-kubernetes/-/tree/master/module-5/Homework

# 5.5 Практическая работа
### Цель домашнего задания
В этом модуле мы узнали про сетевую подсистему Кубернетеса и о том, как сделать pods кластера доступными снаружи кластера. Цель этой домашней работы — научиться публиковать pods кластера наружу с помощью сервисов NodePort и Ingress и научиться ограничивать сетевое взаимодействие pods с помощью сетевых политик.

### Примечание: 
Для создания и применения сетевых политик вам понадобится CNI-плагин, который их поддерживает. Один из вариантов — Calico. Minikube с поддержкой Calico можно запустить следующим образом:
`minikube start --cni calico`

### Введение
Ваша компания разрабатывает новый REST-сервис billing — приложение на Python, сохраняющее историю платежей пользователей в базу postgres. База находится в кластере в том же неймспейсе, что и само приложение, и недоступна снаружи кластера. 


## Задание 1
Один из QA-инженеров подозревает, что сервис работает неправильно. Поэтому он просит вас открыть прямой доступ к базе из локальной сети для проверки записей в базе вручную.

### Что нужно сделать
Опубликуйте доступ к базе по порту 30007 на хостах кластера с помощью сервиса NodePort.

Разверните приложение в кластере.
Перейдите в GitLab Skillbox по кнопке внизу.
В папке module-5/Homework/billing/app находится приложение billing. Оно представляет собой веб-сервер на Flask, «слушающий» на порту 8080 и имеющий следующие эндпоинты:
```
GET:
/ping — возвращает строку «pong»;
/getall — возвращает список всех записей в базе;
/get/<id> — возвращает запись по конкретному id.
POST:
/add — создаёт новую запись. Параметры запроса:
client_id — id клиента;
amount — размер платежа.
```
Примеры запросов :
```
curl http://127.0.0.1:8080/getall       ### Запрашивает все записи в базе
curl http://127.0.0.1:8080/get/1        ### Запрашивает запись с id 1
curl -X POST http://127.0.0.1:8080/add?client_id=1\&amount=100 ### Создает новую запись с client_id=1 и amount=100
```

### Соберите приложение:

`docker build -t billing:v1.0`
Загрузите полученный образ в ваш Docker Registry. В случае с Minikube это можно сделать так:

`minikube image load billing:v1.0`


В директории module-5/Homework/billing находятся манифесты деплойментов базы, самого приложения и их сервисы. Создайте объекты в кластере:
```
kubectl create -f db.yaml
kubectl create -f app.yaml
```

Проверьте, что сервис корректно запустился и работает. Для этого создайте рядом вспомогательный pod:

`kubectl run tmp-pod --rm -i --tty --image nicolaka/netshoot -- /bin/bash`


И протестируйте его эндпоинты:

Создайте новую транзакцию командой:
curl -X POST http://billing:8080/add?client_id=1\&amount=1000
И запросите её детальную информацию:
curl http://billing:8080/get/1 


С помощью сервиса типа NodePort опубликуйте базу наружу на порту 30007. Убедитесь, что порт базы опубликован. Для этого можно узнать IP-адрес одной из нод:

kubectl get nodes -o wide
    И запустить telnet на нужный порт:

        telnet <INTERNAL-IP> 30007


### Что оценивается

Корректность манифеста Service типа nodePort. 



### Как отправить задание на проверку

Пришлите yaml-файлы с манифестом сервиса через форму ниже.


## Задание 2
QA-инженер сообщил вам, что сервис работает корректно, и попросил сделать его доступным для внешних потребителей. 

### Что нужно сделать

Опубликуйте сервис billing наружу кластера с помощью ingress.

Установите ingress в вашем кластере. В Minikube это можно сделать одной командой:
minikube addons enable ingress
После выполнения этой команды Minikube создаст новый неймспейс ingress-nginx, установит туда контроллер nginx ingress и откроет его во внешний мир через сервис NodePort.

Создайте объект ingress с именем services со следующими параметрами:
Ingress должен содержать всего одно правило, по которому все запросы на эндпоинт /billing/* (например, /billing/getall ) должны перенаправляться в сервис billing на порт 8080.
Обратите внимание, что на сервис должны приходить запросы без префикса /billing/, потому что сервис ничего не знает о нём. Таким образом, запросы типа /billing/getall, пройдя через ingress-controller, должны быть переписаны в виде /getall.
Hint: для такого рода операций можно использовать аннотации ingress.

Проверьте правильность работы Ingress. Для этого в случае с Minikube узнайте его внешний адрес:
minikube ip
И отправьте запросы на сервис:

curl http://<MINIKUBE IP>/billing/getall
Приходящие на сервис запросы вы можете отслеживать через логи его pod:

        kubectl logs billing-***


### Что оценивается

Корректность объекта Ingress.



### Как отправить задание на проверку

Пришлите yaml-файл с манифестом Ingress через форму ниже.



## Задание 3
### Что нужно сделать

Вы совместно с отделом безопасности решаете ограничить доступ других приложений к сервису billing и его базе, чтобы никто не мог внести изменения в историю платежей. Для этого вам нужно создать одну общую запретительную политику, запрещающую все сетевые подключения к pods в неймспейсе, и одну разрешительную политику, которая бы разрешала подключения из сервиса billing к базе.

Для корректного применения политик удалите все pods приложения. Это можно сделать, скалировав число pods до нуля:
kubectl scale --replicas=0 deployment/billing
Примените общую запретительную политику. Она запрещает все сетевые подключения в неймспейсе. Для этого примените файл module-5/Homework/task3/deny_all.yaml:
kubectl create -f deny_all.yaml
Теперь скалируйте деплоймент приложения billing до одной реплики:
kubectl scale --replicas=1 deployment/billing
init-контейнер pod не может успешно отработать, потому что база недоступна. В логах billing можно увидеть:

check-db-ready postgres:5432 - no response                                                                                                                                
check-db-ready database is not ready 
Для того, чтобы разрешить сетевое взаимодействие billing → postgres, создайте разрешительную политику. Используйте для этого селекторы типа matchLabels, в которых указаны селекторы приложений.
Обратите внимание, что доступ нужно открыть только для подключений от сервиса billing к базе postgres, и только по порту 5432.

Примените политику к кластеру. Проверить, что доступ заработал, можно по успешно отработавшему init-контейнеру, а также подключившись внутрь pod и выполнив любой запрос (например, запросив список всех транзакций):
kubectl exec -ti deployments/billing  -- bash
apt update && apt install -y curl
curl http://127.0.0.1:8080/getall
