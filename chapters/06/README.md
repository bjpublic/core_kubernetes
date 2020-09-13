# 6. 쿠버네티스 네트워킹

## 6.1 Service 소개

```bash
kubectl run mynginx --image nginx
# pod/mynginx created

# Pod IP는 사용자마다 다릅니다.
kubectl get pod -owide
# NAME     READY   STATUS     RESTARTS   AGE   IP           NODE    ...
# mynginx  1/1     Running    0          12d   10.42.0.26   master  ...

kubectl exec mynginx -- curl -s 10.42.0.26
# <html>
# <head>
# <title>Welcome to nginx!</title>
# <style>
#     body {
# ...
```

### 6.1.3 Service 첫 만남

```yaml
# myservice.yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    hello: world
  name: myservice
spec:
  ports:
  - port: 8080
    protocol: TCP
    targetPort: 80
  selector:
    run: mynginx
```

#### 라벨 셀렉터를 이용하여 `Pod`를 선택하는 이유

```bash
# 앞에서 살펴 본 Service 리소스를 생성합니다.
kubectl apply -f myservice.yaml
# service/myservice created

# 생성된 Service 리소스를 조회합니다.
# Service IP (CLUSTER-IP)를 확인합니다. (예제에서는 10.43.152.73)
kubectl get service  # 축약 시, svc
# NAME          TYPE        CLUSTER-IP     EXTERNAL-IP  PORT(S)    AGE
# kubernetes    ClusterIP   10.43.0.1      <none>       443/TCP    24d
# myservice     ClusterIP   10.43.152.73   <none>       8080/TCP   6s

# Pod IP를 확인합니다. (예제에서는 10.42.0.226)
kubectl get pod -owide
# NAME     READY  STATUS    RESTARTS   AGE   IP            NODE   ...
# mynginx  1/1    Running   0          6s    10.42.0.226   master ...
```

```bash
# curl 요청할 client Pod 생성
kubectl run client --image nginx
# pod/client created

# Pod IP로 접근
kubectl exec client -- curl -s 10.42.0.226

# Service IP로 접근 (CLUSTER-IP)
kubectl exec client -- curl -s 10.43.152.73:8080

# Service 이름 (DNS 주소)로 접근
kubectl exec client -- curl -s myservice:8080
```

```bash
# DNS lookup을 수행하기 위해 nslookup 명령을 설치합니다.
kubectl exec client -- sh -c "apt update && apt install -y dnsutils"
# Hit:1 http://deb.debian.org/debian buster InRelease
# Hit:2 http://security.debian.org/debian-security buster/updates 
# Reading package lists...
# ...

# myservice의 DNS를 조회합니다.
kubectl exec client -- nslookup myservice
# Server:         10.43.0.10
# Address:        10.43.0.10#53
# 
# Name:   myservice.default.svc.cluster.local
# Address: 10.43.152.73
```
### 6.1.4 `Service` 도메인 주소 법칙

```bash
# Service의 전체 도메인 주소를 조회합니다.
kubectl exec client -- nslookup myservice.default.svc.cluster.local
# Server:         10.43.0.10
# Address:        10.43.0.10#53
# 
# Name:   myservice.default.svc.cluster.local
# Address: 10.43.152.73

# Service의 도메인 주소 일부를 생략하여 조회합니다.
kubectl exec client -- nslookup myservice.default
# Server:         10.43.0.10
# Address:        10.43.0.10#53
# 
# Name:   myservice.default.svc.cluster.local
# Address: 10.43.152.73

# Service 이름만 사용해도 참조가 가능합니다.
kubectl exec client -- nslookup myservice
# Server:         10.43.0.10
# Address:        10.43.0.10#53
# 
# Name:   myservice.default.svc.cluster.local
# Address: 10.43.152.73
```

### 6.1.5 클러스터 DNS 서버

```bash
# 로컬 호스트 서버의 DNS 설정이 아닌 Pod의 DNS 설정을 확인합니다.
kubectl exec client -- cat /etc/resolv.conf
# nameserver 10.43.0.10
# search default.svc.cluster.local svc.cluster.local cluster.local ap-northeast-2.compute.internal
# options ndots:5
```

```bash
kubectl get svc -n kube-system
# NAME      TYPE       CLUSTER-IP   EXTERNAL-IP  PORT(S) 
# kube-dns  ClusterIP  10.43.0.10   <none>       53/UDP,53/TCP,9153/TCP 
```

```bash
kubectl get svc kube-dns -nkube-system --show-labels
# NAME       TYPE         CLUSTER-IP  ...    AGE   LABELS
# kube-dns   ClusterIP    10.43.0.10  ...    46h   k8s-app=kube-dns,...
```

```bash
kubectl get pod -n kube-system -l k8s-app=kube-dns
# NAME              READY   STATUS    RESTARTS   AGE
# coredns-6c6bb68   1/1     Running   0          46h
```

## 6.2 Service 종류

### 6.2.1 ClusterIP

```bash
kubectl run cluster-ip --image nginx --expose --port 80 \
    --dry-run=client -o yaml > cluster-ip.yaml

vim cluster-ip.yaml
```

```yaml
# cluster-ip.yaml
apiVersion: v1
kind: Service
metadata:
  name: cluster-ip
spec:
  # type: ClusterIP  # 생략되어 있음
  ports:
  - port: 8080
    protocol: TCP
    targetPort: 80
  selector:
    run: cluster-ip
---
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: cluster-ip
  name: cluster-ip
spec:
  containers:
  - image: nginx
    name: nginx
    ports:
    - containerPort: 80
```

```bash
kubectl apply -f cluster-ip.yaml
# service/cluster-ip created
# pod/cluster-ip created

kubectl get svc cluster-ip -oyaml | grep type
#  type: ClusterIP

kubectl exec client -- curl -s cluster-ip
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...
```

### 6.2.2 NodePort

```yaml
# node-port.yaml
apiVersion: v1
kind: Service
metadata:
  name: node-port
spec:
  type: NodePort     # type 추가
  ports:
  - port: 8080
    protocol: TCP
    targetPort: 80
    nodePort: 30080  # 호스트(노드)의 포트 지정
  selector:
    run: node-port
---
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: node-port
  name: node-port
spec:
  containers:
  - image: nginx
    name: nginx
    ports:
    - containerPort: 80
```

```bash
kubectl apply -f node-port.yaml
# service/node-port created
# pod/node-port created

kubectl get svc
# NAME         TYPE        CLUSTER-IP     EXTERNAL-IP  PORT(S)         AGE
# kubernetes   ClusterIP   10.43.0.1      <none>       443/TCP         26d
# myservice    ClusterIP   10.43.152.73   <none>       8080/TCP        2d
# cluster-ip   ClusterIP   10.43.9.166    <none>       8080/TCP        42h
# node-port    NodePort    10.43.94.27    <none>       8080:30080/TCP  42h
```

```bash
# 트래픽을 전달 받을 Pod가 마스터 노드에 위치합니다.
kubectl get pod node-port -owide
# NAME         READY   STATUS    RESTARTS   AGE   IP           NODE   
# node-port    1/1     Running   0          14m   10.42.0.28   master

MASTER_IP=$(kubectl get node master -ojsonpath="{.status.addresses[0].address}")
curl $MASTER_IP:30080
# <!DOCTYPE html>
# <html>
# <head>
# ...

WORKER_IP=$(kubectl get node worker -ojsonpath="{.status.addresses[0].address}")
curl $WORKER_IP:30080
# <!DOCTYPE html>
# <html>
# <head>
# ...
```

```bash
curl <공인IP>:30080

# 웹 브라우저에서 <공인IP>:30080으로도 확인할 수 있습니다.
```

### 6.2.3 LoadBalancer

```yaml
# load-bal.yaml
apiVersion: v1
kind: Service
metadata:
  name: load-bal
spec:
  type: LoadBalancer  # 타입 LoadBalancer
  ports:
  - port: 8080
    protocol: TCP
    targetPort: 80
    nodePort: 30088   # 30088로 변경
  selector:
    run: load-bal
---
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: load-bal
  name: load-bal
spec:
  containers:
  - image: nginx
    name: nginx
    ports:
    - containerPort: 80
```

```bash
kubectl apply -f load-bal.yaml
# service/load-bal created
# pod/load-bal created

kubectl get svc load-bal
# NAME         TYPE          CLUSTER-IP    EXTERNAL-IP    PORT(S)         
# load-bal     LoadBalancer  10.43.230.45  10.0.1.1       8080:30088/TCP  
```

```bash
# <로드밸런서IP>:<Service Port>로 호출합니다.
curl 10.0.1.1:8080
```

```bash
kubectl get pod
# NAME                   READY   STATUS    RESTARTS   AGE
# ...
# svclb-load-bal-5n2z8   1/1     Running   0          4m
# svclb-load-bal-svv8j   1/1     Running   0          4m
```

### 6.2.4 ExternalName

```yaml
# external.yaml
apiVersion: v1
kind: Service
metadata:
  name: google-svc  # 별칭
spec:
  type: ExternalName
  externalName: google.com  # 외부 DNS
```

```bash
kubectl apply -f external.yaml
# service/google-svc created

kubectl run call-google --image curlimages/curl \
              --  curl -s -H "Host: google.com" google-svc
# pod/call-google created

kubectl logs call-google
# <HTML><HEAD><meta http-equiv="content-type" content="text/..">
# <TITLE>301 Moved</TITLE></HEAD><BODY>
# <H1>301 Moved</H1>
# ...
```

## 참고할 자료

- 네트워크 구조: [https://kubernetes.io/docs/concepts/cluster-administration/networking/#the-kubernetes-network-model](https://kubernetes.io/docs/concepts/cluster-administration/networking/#the-kubernetes-network-model)
- 쿠버네티스 네트워킹 이해하기: [https://coffeewhale.com/k8s/network/2019/04/19/k8s-network-01](https://coffeewhale.com/k8s/network/2019/04/19/k8s-network-01)


### Clean up

```bash
kubectl delete svc --all
kubectl delete pod --all
```
