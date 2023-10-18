# Homework №1
1. `docker build -t poder:v1.0 --build-arg http_proxy= --build-arg https_proxy= .` - build without proxy
2. `minikube image load poder:v1.0` - add image
3. `kubectl create -f poder.yaml` - add pod
4. `kubectl run tmp-pod --rm -i --tty --image nicolaka/netshoot -- /bin/bash` - create tmp pod
5. `curl http://poder:8080/pods` - check permissions
6. `vi role-list-pod.yaml` - add list pods role
7. `vi rolebinding-role-list.yaml` - bind role pod-viewer to default NS
8. `kubectl apply -f role-list-pod.yaml -f rolebinding-role-list.yaml` - add objects
9. `kubectl run tmp-pod --rm -i --tty --image nicolaka/netshoot -- /bin/bash` - create tmp pod 
    1. `curl http://poder:8080/pods` - {"pods":["poder","tmp-pod"]} - check permissions
