# K8s config:

Cache --> Ansible dynamic inventory --> Cluster_1 (host1, host2)
Cache --> Ansible dynamic inventory --> Cluster_2 (host3, host4)
Cache --> Ansible dynamic inventory --> Cluster_3 (host5, host6)

### Config Maps:
1. Это источник значений переменной среды.
2. Служит для переиспользования манифестов в prod/dev/test NS

# Create ConfigMap:
1. `kubectl apply -f node-hello-cm.yaml` - create cm
2. `kubectl describe configmaps demo-app-config` - describe cm
3. `kubectl exec -ti demo-app -n test -- printenv | grep .env` - check cm config

# Create Secrets:
Типы:
- Opaque - самый общий тип секрета создаваемый по-умолчанию
- kubernetes.io/service-account-token - использ-ся для хранения токенов спец УЗ
### - kubernetes.io/dockercfg - содержит имя доступа и пароль приватного docker-registry
- kubernetes.io/basic-auth - использ-ся для авторизации
- kubernetes.io/ssh-auth - использ-ся для авторизации
- kubernetes.io/tls - использ-ся для хранения tls ключей
- bootstrap.kubernetes.io/token - использ-ся в процессе подкл-ия Node 

Prod решения используют hashicorp vault или облачные провайдеры (aws secrets manager)


1. `kubectl apply -f admin.yaml` - create secret
2. `kubectl get secret` - list secrets
3. `kubectl describe secret mysecret` - secret info
4. `kubectl create secret generic user-creds --from-file=./username.txt --from-file=./password.txt` - create secret from files