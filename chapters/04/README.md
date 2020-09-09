# 4. 쿠버네티스 첫 만남

## 4.1 기본 명령

### 4.1.1 컨테이너 실행

```bash
kubectl run mynginx --image nginx
# pod/mynginx created
```

### 4.1.2 컨테이너 조회

```bash
kubectl get pod
# NAME      READY   STATUS    RESTARTS   AGE
# mynginx   1/1     Running   0          2s
```

```bash
kubectl get pod mynginx -o yaml
# apiVersion: v1
# kind: Pod
# metadata:
#   creationTimestamp: "2020-06-21T06:54:52Z"
#   labels:
#     run: mynginx
#   managedFields:
#   - apiVersion: v1
#   ...
#   ...
#   name: mynginx
#   namespace: default
#   resourceVersion: "11160054"
#   ...
```

```bash
kubectl get pod -o wide
# NAME     READY   STATUS    RESTARTS   AGE  IP            NODE    ...
# mynginx  1/1     Running   0          6s   10.42.0.226   worker  ...
```

### 4.1.3 컨테이너 상세 정보 확인

```bash
kubectl describe pod mynginx
# Name:         mynginx
# Namespace:    default
# Priority:     0
# Node:         worker/10.0.1.2
# Start Time:   Sun, 21 Jun 2020 06:54:52 +0000
# Labels:       run=mynginx
# Annotations:  <none>
# Status:       Running
# IP:           10.42.0.155
# IPs:
#   IP:  10.42.0.155
# ....
```

### 4.1.4 컨테이너 로깅

```bash
kubectl logs -f mynginx
# /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will ...
# /docker-entrypoint.sh: Looking for shell scripts in /docker-...
# ...
```

### 4.1.5 컨테이너 명령 전달

```bash
# mynginx에 apt-update 명령을 전달합니다.
kubectl exec mynginx -- apt-get update
# Get:1 http://security.debian.org/debian-security buster/updates ...
# Get:2 http://deb.debian.org/debian buster InRelease [121 kB]
# Get:3 http://deb.debian.org/debian buster-updates InRelease [51.9 kB]
# ...
```

```bash
kubectl exec -it mynginx -- bash

$root@mynginx:/# hostname
# mynginx

# 컨테이너 exit
$root@mynginx:/# exit
```

### 4.1.6 컨테이너 / 호스트간 파일 복사

```bash
# <HOST> --> <CONTAINER>
kubectl cp /etc/passwd mynginx:/tmp/passwd

# exec 명령으로 복사가 되었는지 확인합니다.
kubectl exec mynginx -- ls /tmp/passwd
# /tmp/passwd

kubectl exec mynginx -- cat /tmp/passwd
# root:x:0:0:root:/root:/bin/bash
# daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
# bin:x:2:2:bin:/bin:/usr/sbin/nologin
# ...
```

### 4.1.7 컨테이너 정보 수정

```bash
kubectl edit pod mynginx
# apiVersion: v1
# kind: Pod
# metadata:
#   creationTimestamp: "..."
#   labels:
#     hello: world        # <-- 라벨 추가
#     run: mynginx
#   managedFields:
#   ...
```

```bash
# mynginx 상세 정보 조회
kubectl get pod mynginx -oyaml
# apiVersion: v1
# kind: Pod
# metadata:
#   creationTimestamp: "..."
#   labels:
#     hello: world        # <-- 추가된 라벨 학인
#     run: mynginx
#   ...
```

### 4.1.8 컨테이너 삭제

```bash
kubectl delete pod mynginx
# pod mynginx deleted

kubectl get pod
# No resources found ..
```

### 4.1.9 선언형 명령 정의서 (YAML) 기반의 컨테이너 생성

```yaml
# mynginx.yaml
apiVersion: v1
kind: Pod
metadata:
  name: mynginx
spec:
  containers: 
  - name: mynginx
    image: nginx
```

```bash
ls
# mynginx.yaml

kubectl apply -f mynginx.yaml
# pod/mynginx created

kubectl get pod 
# NAME      READY   STATUS      RESTARTS   AGE
# mynginx   1/1     Running     1          6s

kubectl get pod mynginx -oyaml
# apiVersion: v1
# kind: Pod
# metadata:
#   ...
#   name: mynginx
#   ...
# spec:
#   containers:
#   - image: nginx
#     name: mynginx
#   ...
```

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/website/master/content/en/examples/pods/simple-pod.yaml
# pod/nginx created

kubectl delete -f https://raw.githubusercontent.com/kubernetes/website/master/content/en/examples/pods/simple-pod.yaml
# pod/nginx deleted
```

```yaml
# mynginx.yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    hello: world          # <-- 라벨 추가
  name: mynginx
spec:
  containers: 
  - name: mynginx
    image: nginx:1.17.2   # <-- 기존 latest에서 1.17.2로 변경
```

```bash
kubectl apply -f mynginx.yaml
# pod/mynginx configured

kubectl get pod 
# NAME      READY   STATUS      RESTARTS   AGE
# mynginx   1/1     Running     1          3m48s

kubectl get pod mynginx -oyaml
# apiVersion: v1
# kind: Pod
# metadata:
#   labels:
#     hello: world
#   ...
#   name: mynginx
#   ...
# spec:
#   containers:
#   - image: nginx:1.17.2
#     name: mynginx
#   ...
```

```bash
kubectl apply -f mynginx.yaml
# pod/mynginx unchanged

kubectl get pod 
# NAME      READY   STATUS      RESTARTS   AGE
# mynginx   1/1     Running     1          3m48s

kubectl get pod mynginx -oyaml
# apiVersion: v1
# kind: Pod
# metadata:
#   labels:
#     hello: world
#   ...
#   name: mynginx
#   ...
# spec:
#   containers:
#   - image: nginx:1.17.2
#     name: mynginx
#   ...
```

## 4.2 고급 명령

### 4.2.1 리소스별 명령

```bash
kubectl get service
# NAME         TYPE       CLUSTER-IP   EXTERNAL-IP   PORT(S)  AGE
# kubernetes   ClusterIP  10.43.0.1    <none>        443/TCP  13d

# describe 명령도 동일하게 작동합니다.
kubectl describe service kubernetes
# Name:              kubernetes
# Namespace:         default
# Labels:            component=apiserver
#                    provider=kubernetes
#  ...
```

```bash
kubectl get node
# NAME     STATUS   ROLES    AGE   VERSION
# master   Ready    master   13d   v1.18.6+k3s1
# worker   Ready             13d   v1.18.6+k3s1

kubectl describe node master
# Name:               master
# Roles:              master
# Labels:             beta.kubernetes.io/arch=amd64
#                     beta.kubernetes.io/instance-type=k3s
# ...
```

### 4.2.2 네임스페이스

```bash
kubectl get namespace
# NAME             STATUS   AGE
# default          Active   12m
# kube-system      Active   12m
# kube-public      Active   12m
# kube-node-lease  Active   12m 

kubectl describe namespace kube-system
# Name:         kube-system
# Labels:       <none>
# Annotations:  <none>
# ...
```

```bash
kubectl run mynginx-ns --image nginx --namespace kube-system
# pod/mynginx-ns created

# kube-system 네임스페이스에서 Pod 확인
kubectl get pod mynginx-ns -n kube-system  # --namespace를 -n로 축약 가능
# NAME        READY   STATUS    RESTARTS   AGE
# mynginx-ns  1/1     Running   0          13s

kubectl delete pod mynginx-ns -n kube-system
# pod/mynginx-ns deleted
```

```bash
kubectl get pod -n default
# NAME      READY   STATUS    RESTARTS   AGE
# mynginx   1/1     Running   0          71m

kubectl get pod
# NAME      READY   STATUS    RESTARTS   AGE
# mynginx   1/1     Running   0          71m
```

### 4.2.3 자동완성 기능

[https://kubernetes.io/docs/tasks/tools/install-kubectl/#enabling-shell-autocompletion](https://kubernetes.io/docs/tasks/tools/install-kubectl/#enabling-shell-autocompletion)

```bash
echo 'source <(kubectl completion bash)' >> ~/.bashrc
source ~/.bashrc
```

```bash
kubectl run yournginx --image nginx
# pod/yournginx created
```

```bash
kubectl get pod <TAB>
# mynginx     yournginx
```

### 4.2.4 즉석 리소스 생성 

```bash
# 즉석에서 YALM 문서를 생성하여 쿠버네티스에게 전달
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: cat-nginx
spec:
  containers:
  - image: nginx
    name: cat-nginx
EOF
# pod/cat-nginx created
```

### 4.2.5 리소스 특정 정보 추출

```bash
kubectl get node master -o yaml
# apiVersion: v1
# kind: Node
# metadata:
#   annotations:
#   ...
# spec:
#   podCIDR: 10.42.0.0/24
#   podCIDRs:
#   - 10.42.0.0/24
#   providerID: k3s://master
# status:
#   addresses:
#   - address: 10.0.1.1
#     type: InternalIP
#   - address: master
#     type: Hostname
```

```bash
kubectl get node master -o wide
# NAME     STATUS   ROLES    AGE   VERSION        INTERNAL-IP     ...
# master   Ready    master   27m   v1.18.6+k3s1   10.0.1.1        ...
```

```bash
kubectl get node master -o jsonpath="{.status.addresses[0].address}"
# 10.0.1.1
```

`jsonpath`에 대한 상세 사용법 참고

[https://kubernetes.io/docs/reference/kubectl/jsonpath](https://kubernetes.io/docs/reference/kubectl/jsonpath/)

### 4.2.6 모든 리소스 조회

```bash
kubectl api-resources
# NAME        SHORTNAMES  APIGROUP  NAMESPACED   KIND
# namespaces  ns                    false        Namespace
# nodes       no                    false        Node
# pods        po                    true         Pod
# ...
```

```bash
kubectl api-resources --namespaced=true 
# NAME          SHORTNAMES   APIGROUP  NAMESPACED   KIND
# bindings                             true         Binding
# configmaps    cm                     true         ConfigMap
# endpoints     ep                     true         Endpoints
# events        ev                     true         Event
```

### 4.2.7 리소스 설명

```bash
# Pod에 대한 정의를 확인할 수 있습니다.
kubectl explain pods
# KIND:     Pod
# VERSION:  v1
# 
# DESCRIPTION:
#      Pod is a collection of containers that can run on a host. 
#      This resource is created by clients and scheduled onto hosts.
# 
# FIELDS:
#    apiVersion   <string>
#      APIVersion defines the versioned schema of this representation 
# ....
```

### 4.2.8 클러스터 상태 확인 

```bash
# 쿠버네티스 API서버 작동 여부 확인
kubectl cluster-info

# 전체 노드 상태 확인
kubectl get node

# 쿠버네티스 핵심 컴포넌트의 Pod 상태 확인
kubectl get pod -n kube-system
```

### 4.2.9 클라이언트 설정파일

```bash
kubectl config view
# apiVersion: v1
# clusters:
# - cluster:
#     certificate-authority-data: DATA+OMITTED
#     server: https://127.0.0.1:6443
#   name: default
# ...
```

```bash
cat $HOME/.kube/config
# apiVersion: v1
# clusters:
# - cluster:
#     certificate-authority-data: ....
#     server: https://127.0.0.1:6443
#   name: default
# contexts:
# - context:
#     cluster: default
#     user: default
#   name: default
# current-context: default
# kind: Config
# preferences: {}
# users:
# - name: default
#   user:
#     password: ...
#     username: admin
```

### 4.2.10 `kubectl` 명령 치트시트

[https://kubernetes.io/docs/reference/kubectl/cheatsheet/](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

### Clean Up

```bash
kubectl delete pod --all
```