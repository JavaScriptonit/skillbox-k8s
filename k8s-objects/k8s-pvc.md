# PV и PVC:
https://go.skillbox.ru/education/course/devops-kubernetes/a0488f3d-8173-4776-bd08-37be12f00ade/videolesson

1. PV
2. PVC

## Типы volumes:
1. in-tree - эти плагины разрабатываются и поставляются с бинарниками k8s. Идут из под коробки
2. csi - container storage interface - эти плагины устанавливаются в k8s отдельно

## Плагины in-tree:
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

## CSI-плагины:
1. Dell EMC: 
Этот CSI-плагин предоставляет интеграцию с хранилищем данных Dell EMC, позволяя использовать его для создания и управления блочного хранилища в Kubernetes. Особенностью плагина является поддержка различных технологий и функций, таких как репликация данных, сжатие и дедупликация.

2. DigitalOcean Block Storage: 
Этот CSI-плагин предоставляет интеграцию с DigitalOcean Block Storage, позволяя создавать и управлять блочным хранилищем на платформе DigitalOcean. Особенностью плагина является простота в использовании и возможность масштабирования блочного хранилища.

3. NetApp: 
Этот CSI-плагин обеспечивает интеграцию с хранилищем данных NetApp, позволяя создавать и управлять блочным хранилищем в Kubernetes. Особенностью плагина является поддержка различных технологий NetApp, таких как Snapshot и FlexClone, а также возможность управления емкостью хранилища через интерфейс Kubernetes.

4. GlusterFS: 
Этот CSI-плагин предоставляет интеграцию с распределенной файловой системой GlusterFS, позволяя использовать его для создания и управления файловым хранилищем в Kubernetes. Особенностью плагина является поддержка масштабирования и отказоустойчивости GlusterFS, а также возможность предоставления доступа к файловому хранилищу для нескольких подов одновременно.

5. IBM Block Storage: 
Этот CSI-плагин обеспечивает интеграцию с блочным хранилищем IBM, позволяя создавать и управлять блочным хранилищем в Kubernetes. Особенностью плагина является поддержка различных функций IBM блочного хранилища, таких как шифрование данных и мониторинг производительности.

https://kubernetes-csi.github.io/docs/drivers.html - полный список плагинов

# Create pod with volumes:
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

# Create pod with 2 containers volumes:
1. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/pod_shared_data.yaml` - create 2 containers
2. `kubectl exec -it two-containers -c second-container -- bash`, `tail -f /pod/data/index.html` - посмотреть как обновляется файл /pod/data/index.html во 2ом контейнере
3. `kubectl exec -it two-containers -c first-container -- bash`, `while true; do curl http://localhost;sleep 2;done` - посмотреть обновление даты


# Create configmap:
1. `kubectl create configmap nginx-config --from-file=nginx.conf` - configmap/nginx-config created
2. `kubectl get cm` - nginx-config       1      61s
3. `kubectl get configmaps nginx-config -o yaml` - kind: ConfigMap
4. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/pod_configmap.yaml` - pod/two-containers created
5. `kubectl exec -it two-containers -c first-container -- bash`, `nginx -T` - посмотреть конфигурацию nginx
6. `kubectl exec -it two-containers -c first-container -- bash`, `while true; do curl http://localhost:8080;sleep 2;done`

# Recreate configmap:
1. `kubectl delete configmap nginx-config` - delete old config (configmap "nginx-config" deleted)
2. `kubectl create configmap nginx-config --from-file=nginx.conf` - configmap/nginx-config created
3. `kubectl apply -f /Users/aashabunov/IdeaProjects/kubernetes/volumes/pod_configmap.yaml` - pod/two-containers created
