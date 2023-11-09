# Volumes:
https://go.skillbox.ru/education/course/devops-kubernetes/a0488f3d-8173-4776-bd08-37be12f00ade/videolesson
## Типы volumes:
1. in-tree - эти плагины разрабатываются и поставляются с бинарниками k8s. Идут из под коробки
2. csi - container storage interface - эти плагины устанавливаются в k8s отдельно

### Плагины in-tree:
Тесно связаны с подом. Создаются и удаляются с подом
1. Ephemeral (эфимерные):
    1. emptyDir
    2. configMap, secret
    3. downwardAPI

Данные сохраняются в независимости от пода
2. Persistant (Постоянные):
    1. awsElasticBlockStore, AzureDisk, gcePersistentDisk
    2. hostPath, nfs, iscsi, rbd
    3. PersistentVolumeClaim и др.

### CSI-плагины:
1. Dell EMC
2. DigitalOcean Block Storage
3. NetApp
4. GlusterFS
5. IBM Block Storage и др.

https://kubernetes-csi.github.io/docs/drivers.html - полный список плагинов

## Create pod with volumes:
1. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/pod_2_volumes.yaml`
2. `kubectl exec -it pod/volumes-pod-2 bash` - bash created pod
3. `df -aTh | grep mnt` - check volumes:
```
overlay        overlay   59G   46G  9.6G  83% /mnt/slow-persistent
tmpfs          tmpfs    7.7G     0  7.7G   0% /mnt/fast-ephemeral
```
4. `for dir in /mnt/*;do echo $dir; dd if=/dev/zero of=$dir/test.delme bs=128k count=32k;done` - команда выполняет следующие действия:
    1. Перебирает все каталоги в `/mnt/` с помощью цикла `for`.
    2. Для каждого каталога, команда echo `$dir` выводит путь к каталогу.
    3. Команда `dd if=/dev/zero of=$dir/test.delme bs=128k count=32k` создает файл `test.delme` размером 4МБ (128кб * 32к).
        1. `if=/dev/zero` указывает использовать нулевое устройство в качестве источника данных.
        2. `of=$dir/test.delme` указывает путь и имя файла, который будет создан.
        3. `bs=128k` указывает размер блока данных, который будет записан в файл.
        4. `count=32k` указывает количество блоков данных, которые будут записаны в файл.
5. `kubectl get po -o wide -n default` - посмотреть на какой ноде запущен под `volumes-pod-2`:
```
volumes-pod-2               1/1     Running   0          6m27s   10.244.1.16   minikube-m02   <none>           <none>
```
6. `docker exec -it minikube-m02 bash` - bash minikube node
7. `ls -la /mnt/hostpath`:
```
-rw-r--r-- 1 root root 4294967296 Nov  8 17:34 test.delme
```

### Create pod with 2 containers volumes:
1. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/pod_shared_data.yaml` - create 2 containers
2. `kubectl exec -it two-containers -c second-container -- bash`, `tail -f /pod/data/index.html` - посмотреть как обновляется файл /pod/data/index.html во 2ом контейнере
3. `kubectl exec -it two-containers -c first-container -- bash`, `while true; do curl http://localhost;sleep 2;done` - посмотреть обновление даты


### Create configmap:
1. `kubectl create configmap nginx-config --from-file=nginx.conf` - configmap/nginx-config created
2. `kubectl get cm` - nginx-config       1      61s
3. `kubectl get configmaps nginx-config -o yaml` - kind: ConfigMap
4. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/pod_configmap.yaml` - pod/two-containers created
5. `kubectl exec -it two-containers -c first-container -- bash`, `nginx -T` - посмотреть конфигурацию nginx
6. `kubectl exec -it two-containers -c first-container -- bash`, `while true; do curl http://localhost:8080;sleep 2;done`

#### Recreate configmap:
1. `kubectl delete configmap nginx-config` - delete old config (configmap "nginx-config" deleted)
2. `kubectl create configmap nginx-config --from-file=nginx.conf` - configmap/nginx-config created
3. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/pod_configmap.yaml` - pod/two-containers created



## PV и PVC. Заявки на хранилища и dynamic provision:
https://go.skillbox.ru/education/course/devops-kubernetes/f02e7585-8216-4965-9f6a-b1520dc5c01e/videolesson
1. PV
2. PVC

### NFS volumes:
Пример: /Users/aashabunov/IdeaProjects/kubernetes/volumes/nfs/nfs_volume.yaml
Недостаток монтирования volumes в pod: Тот кто пишет спецификацию pod - должен знать фактическую инфраструктуру хранилищ

1. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/nfs/pv.yaml` - persistentvolume/volume-slow created
2. `kubectl get pv`:
```
NAME          CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   REASON   AGE
volume-slow   10Gi       RWO            Retain           Available                                   62s
```
    1. STATUS: Available - если не востребован ни 1ой заявкой
3. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/nfs/pvc.yaml` - persistentvolumeclaim/pvc-slow created
4. `kubectl get pvc`, `kubectl get pv`:
```
NAME       STATUS   VOLUME        CAPACITY   ACCESS MODES   STORAGECLASS   AGE
pvc-slow   Bound    volume-slow   10Gi       RWO                           22s

NAME          CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM              STORAGECLASS   REASON   AGE
volume-slow   10Gi       RWO            Retain           Bound    default/pvc-slow                           5m42s
```
5. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/nfs/pod_pvc.yaml` - pod/pod-pvc created
6. `kubectl exec -it pod-pvc bash`, `df -H`:
```
Filesystem      Size  Used Avail Use% Mounted on
overlay          63G   50G   11G  83% /cache
```


### StorageClass:
1. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/storage-class/sc.yaml` - storageclass.storage.k8s.io/local-host-path created
2. `kubectl get sc`:
```
NAME                 PROVISIONER                       RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
local-host-path      kubernetes.io/minikube-hostpath   Retain          Immediate           true                   12s
standard (default)   k8s.io/minikube-hostpath          Delete          Immediate           false                  12d
```
3. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/storage-class/pvc_storage_class.yaml` - persistentvolumeclaim/pvc-slow created
4. `kubectl get pvc`:
```
NAME       STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS      AGE
pvc-slow   Pending                                      local-host-path   48s
```
#### Debug:
5. `kubectl get pvc/pvc-slow -o yaml` - вывод yaml созданного VPC
6. `kubectl describe pvc pvc-slow`:
```
Warning  ProvisioningFailed  7s (x6 over 72s)  persistentvolume-controller  no volume plugin matched name: kubernetes.io/minikube-hostpath
```
7. `kubectl delete -f pvc_storage_class.yaml`, `kubectl delete -f sc.yaml`, `kubectl apply -f pvc_storage_class.yaml` - пересоздать PVC повторно после изменения PVC: `storageClassName: "local-host-path"` на `storageClassName: standard` и использования стандартного storageclass, который создается автоматически при установке Minikube
8. `kubectl get pvc -o wide`:
```
NAME       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE   VOLUMEMODE
pvc-slow   Bound    pvc-200a26d4-42e6-4690-9169-7826ea5f7be2   10Gi       RWO            standard       13s   Filesystem
```
9. `kubectl get pv` - проверить созданный VOLUME:
```
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM              STORAGECLASS   REASON   AGE
pvc-200a26d4-42e6-4690-9169-7826ea5f7be2   10Gi       RWO            Delete           Bound    default/pvc-slow   standard                3m59s
```
### Create pod:
10. `kubectl apply -f pod_sc_pvc.yaml` - pod/pod-sc-pvc created
11. `kubectl exec -it pod/pod-sc-pvc bash`, `df -H` - проверить volume

## Change Default SC in cluster:
1. `kubectl patch storageclass standard -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'` - убрать метку default co storageclass:standard
2. `kubectl get sc` - проверить метку
3. `kubectl patch storageclass local-host-path -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'` - поставить метку созданному sc
4. `kubectl get sc` - проверить метку



# StatefulSet:
https://go.skillbox.ru/education/course/devops-kubernetes/6173ce0b-8a49-401d-9517-138c4592a71f/videolesson
StatefulSet в Kubernetes предоставляет средства для запуска и управления подов с уникальными идентификаторами в состоянии, такими как базы данных или очереди сообщений. Основная особенность StatefulSet заключается в том, что он обеспечивает стабильные и уникальные имена и сетевые идентификаторы для каждой реплики пода.

ClusterIP: None указывается в сервисе для того, чтобы не назначать кластерный IP-адрес для сервиса. Вместо этого, каждый под внутри StatefulSet получает свой собственный доменный DNS-адрес в формате <pod-name>.<service-name>.<namespace>.svc.cluster.local. Это позволяет подам внутри StatefulSet обращаться друг к другу с использованием стабильных идентификаторов независимо от порядка их перезапуска или масштабирования.

Это особенно полезно для приложений, которые требуют уникальных и стабильных идентификаторов, например, базы данных, которым необходимы стабильные имена узлов, чтобы обеспечить согласованность данных и возможность выполнения операций отказоустойчиво.

Также, использование StatefulSet позволяет управлять порядком создания и масштабирования подов, а также выполнять ролл-ауты и ролл-бэки подов с сохранением их уникальных идентификаторов. Это обеспечивает стабильность и предсказуемость в работе приложения.

Таким образом, основные преимущества использования StatefulSet включают стабильность и уникальные идентификаторы для реплик подов, возможность обращаться к подам по уникальным именам без необходимости использования IP-адресов, возможность управления порядком создания и масштабирования подов, а также поддержка операций ролл-аута и ролл-бэка с сохранением идентификаторов.

1. `kubectl create deployment nginx --image=nginx --replicas=3` - создать 3 пода с nginx
2. `kubectl get po -o wide`
3. `kubectl expose deployment/nginx --name nginx-normal --port=80 --target-port=80` - создать сервис для nginx с IP адресом
4. `kubectl expose deployment/nginx --name nginx-headless --port=80 --target-port=80 --cluster-ip="None"` - создать сервис для nginx без IP адреса
5. `kubectl describe svc nginx-headless`, `kubectl describe svc nginx-normal` - посмотреть сервисы
6. `kubectl run tmp-pod --rm -i --tty --image nicolaka/netshoot -- /bin/bash`, `nslookup nginx-normal`:
```
Server:         10.96.0.10
Address:        10.96.0.10#53

Name:   nginx-normal.default.svc.cluster.local
Address: 10.100.17.115
```
7. `kubectl run tmp-pod --rm -i --tty --image nicolaka/netshoot -- /bin/bash`, `nslookup nginx-headless`:
Headless сервис отвечает на запрос DNS адресами его подов:
```
Server:         10.96.0.10
Address:        10.96.0.10#53

Name:   nginx-headless.default.svc.cluster.local
Address: 10.244.2.13
Name:   nginx-headless.default.svc.cluster.local
Address: 10.244.1.26
Name:   nginx-headless.default.svc.cluster.local
Address: 10.244.0.21
```

## Принцип работы StatefulSet:
1. Headless service [my-service.default.svc.cluster.local] --> [pod-0.my-service.default.svc.cluster.local] --> [PersistentVolume]
2. `kubectl apply -f cassandra-service.yaml` - service/cassandra created
3. `kubectl apply -f cassandra-statefulset.yaml` - statefulset.apps/cassandra created
4. `kubectl get po -o wide --watch`:
```
NAME          READY   STATUS    RESTARTS      AGE    IP            NODE           NOMINATED NODE   READINESS GATES
cassandra-0   1/1     Running   0             104s   10.244.2.14   minikube-m03   <none>           <none>
cassandra-1   1/1     Running   1 (53s ago)   85s    10.244.1.28   minikube-m02   <none>           <none>
cassandra-2   1/1     Running   0             66s    10.244.0.22   minikube       <none>           <none>
```
5. `kubectl logs --tail 20 cassandra-0` - логи пода (20 последних строчек)
6. `kubectl get pvc`:
```
NAME                         STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
cassandra-data-cassandra-0   Bound    pvc-755dd4cd-e821-4d7e-8968-13f6fe9617cc   1Gi        RWO            standard       6m7s
cassandra-data-cassandra-1   Bound    pvc-04b4088c-41d6-4c78-b631-85015bf3e671   1Gi        RWO            standard       5m48s
cassandra-data-cassandra-2   Bound    pvc-4897d63a-7ab0-47bd-b39b-d8504f8511b3   1Gi        RWO            standard       5m29s
```
7. `kubectl exec -it pod/cassandra-0 bash`, `nodetool status` - 
8. `kubectl exec -it pod/cassandra-0 bash`, `ping cassandra-0.cassandra.default.svc.cluster.local` - [pod-0.my-service.default.svc.cluster.local] 