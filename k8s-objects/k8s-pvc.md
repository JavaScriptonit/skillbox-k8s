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
1. Dell EMC
2. DigitalOcean Block Storage
3. NetApp
4. GlusterFS
5. IBM Block Storage и др.

https://kubernetes-csi.github.io/docs/drivers.html - полный список плагинов