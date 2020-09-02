# 11. 고급 스케줄링

## 11.1 고가용성 확보 - Pod 레벨

### 11.1.1 metrics server 설치

```bash
helm install metrics-server stable/metrics-server \
    --version 2.11.1 \
    --namespace ctrl
# NAME: metrics-server
# LAST DEPLOYED: Wed Jul  8 17:50:32 2020
# NAMESPACE: ctrl
# STATUS: deployed
# REVISION: 1
# NOTES:
# The metric server has been deployed.
# 
# In a few minutes you should be able to list metrics using the following
# command:
# 
#   kubectl get --raw "/apis/metrics.k8s.io/v1beta1/nodes"

# metrics-server가 정상적으로 올라오기까지 시간이 조금 걸립니다.
kubectl get pod -nctrl
# NAME                              READY   STATUS    RESTARTS   AGE
# metrics-server-8555869558-k7gb6   0/1     Running   0          34s
```

```bash
# 리소스 사용량을 모니터링할 Pod를 하나 생성합니다.
kubectl run mynginx --image nginx

# Pod별 리소스 사용량을 확인합니다.
kubectl top pod
# NAME        CPU(cores)   MEMORY(bytes)
# mynginx     0m           2Mi

# Node별 리소스 사용량을 확인합니다.
kubectl top node
# NAME      CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
# master    57m          2%     1846Mi          46%
# worker    43m          2%      970Mi          24%

kubectl delete pod mynginx
# pod/mynginx deleted
```

### 11.1.2 자동 확장할 Pod 생성

```php
# image: k8s.gcr.io/hpa-example
<?php
  $x = 0.0001;
  for ($i = 0; $i <= 1000000; $i++) {
    $x += sqrt($x);
  }
  echo "OK!";
?>
```

```yaml
# heavy-cal.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: heavy-cal
spec:
  selector:
    matchLabels:
      run: heavy-cal
  replicas: 1
  template:
    metadata:
      labels:
        run: heavy-cal
    spec:
      containers:
      - name: heavy-cal
        image: k8s.gcr.io/hpa-example
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: 500m
          requests:
            cpu: 300m
---
apiVersion: v1
kind: Service
metadata:
  name: heavy-cal
spec:
  ports:
  - port: 80
  selector:
    run: heavy-cal
```

```bash
kubectl apply -f heavy-cal.yaml
# deployment.apps/heavy-cal created
# service/heavy-cal created
```

### 11.1.3 `hpa` 생성 - 선언형 명령

```yaml
# hpa.yaml
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: heavy-cal
spec:
  maxReplicas: 50
  minReplicas: 1
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: heavy-cal
  targetCPUUtilizationPercentage: 50
```

```bash
# hpa 리소스 생성
kubectl apply -f hpa.yaml
# horizontalpodautoscaler.autoscaling/heavy-cal autoscaled
```

### 11.1.4 `hpa` 생성 - 명령형 명령

```bash
kubectl autoscale deployment heavy-cal --cpu-percent=50 --min=1 --max=50
# horizontalpodautoscaler.autoscaling/heavy-cal autoscaled

kubectl get hpa
# NAME        REFERENCE                   TARGET    MINPODS  MAXPODS   REPLICAS   AGE
# heavy-cal   Deployment/heavy-cal/scale  0% / 50%  1        50        1          18s
```

### 11.1.5 자동확장 테스트

```yaml
# heavy-load.yaml
apiVersion: v1
kind: Pod
metadata:
  name: heavy-load
spec:
  containers: 
  - name: busybox
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "while true; do wget -q -O- http://heavy-cal; done"]
```

```bash
kubectl apply -f heavy-load.yaml
# pod/heavy-load created

# watch문으로 heavy-cal를 계속 지켜보고 있으면 Pod의 개수가 증가하는 것을 확인할 수 있습니다.
watch kubectl top pod
# NAME                         CPU(cores)   MEMORY(bytes)
# heavy-load                   7m           1Mi
# heavy-cal-548855cf99-9s44l   140m         12Mi
# heavy-cal-548855cf99-lnbvm   122m         13Mi
# heavy-cal-548855cf99-lptbq   128m         13Mi
# heavy-cal-548855cf99-qpdng   89m          12Mi
# heavy-cal-548855cf99-tvgfn   137m         13Mi
# heavy-cal-548855cf99-x64mg   110m         12Mi
```

```bash
kubectl delete pod heavy-load
```

## 11.2 고가용성 확보 - Node 레벨

### 11.2.1 AWS EKS Cluster AutoScaler 설정

```bash
NAME=k8s
REGION=ap-northeast-2

helm install autoscaler stable/cluster-autoscaler \
  --namespace kube-system \
  --set autoDiscovery.clusterName=$NAME,awsRegion=$REGION,sslCertPath=/etc/kubernetes/pki/ca.crt
  --version 7.3.4
```

### 11.2.2 GCP GKE Cluster AutoScaler 설정

```bash
CLUSTER_NAME=k8s
REGION=us-central1-a

gcloud container clusters create $CLUSTER_NAME \
    --enable-autoscaling \
    --min-nodes=1 \
    --num-nodes=2 \
    --max-nodes=4 \
    --node-locations=$CLUSTER_NAME \
    --machine-type=n1-highcpu-8
```

### 11.2.3 Cluster AutoScaling 활용

```bash
# 인위적으로 Pod 증가
kubectl scale deployment heavy-cal --replicas=50
# deployment.apps/heavy-cal scaled

# Pod 리스트
kubectl get pod
# NAME                        READY   STATUS    RESTARTS   AGE
# heavy-cal-548855cf99-x64m   1/1     Running   0          2s
# heavy-cal-548855cf99-dfx2   1/1     Running   0          2s
# heavy-cal-548855cf99-sf3x   1/1     Running   0          2s
# ....
# heavy-cal-548855cf99-a21t   0/1     Pending   0          2s
# heavy-cal-548855cf99-g8ib   0/1     Pending   0          2s
# heavy-cal-548855cf99-b754   0/1     Pending   0          2s
# ...

watch kubectl get node
# NAME             STATUS   ROLES    AGE   VERSION
# ip-172-31-42-5   Ready             13h   v1.18.6
# ip-172-31-44-9   Ready             1m    v1.18.6
# ....             Ready             1m    v1.18.6
# ....
```

### Clean up

```bash
kubectl delete hpa heavy-cal
kubectl delete deploy heavy-cal
kubectl delete svc heavy-cal
```

## 11.3 `Taint & Toleration`

### 11.3.1 Taint

```bash
# taint 방법
kubectl taint nodes $NODE_NAME <KEY>=<VALUE>:<EFFECT>
```

### 11.3.2 Toleration

```bash
# project=A 라는 taint를 NoSchedule로 설정
kubectl taint node worker project=A:NoSchedule
# node/worker tainted

kubectl get node worker -oyaml | grep -A 4 taints
#  taints:
#  - effect: NoSchedule
#    key: project
#    value: A
```

```yaml
# no-tolerate.yaml
apiVersion: v1
kind: Pod
metadata:
  name: no-tolerate
spec:
  containers:
  - name: nginx
    image: nginx
```

```bash
kubectl apply -f no-tolerate.yaml
# pod/no-tolerate created

kubectl get pod -o wide
# NAME         READY   STATUS    RESTARTS  AGE   IP        NODE    ...
# no-tolerate  1/1     Running   0         3s    <none>    master  ... 
```

```yaml
# tolerate.yaml
apiVersion: v1
kind: Pod
metadata:
  name: tolerate
spec:
  containers:
  - name: nginx
    image: nginx
  tolerations:
  - key: "project"
    value: "A"
    operator: "Equal"
    effect: "NoSchedule"
```

```bash
kubectl apply -f tolerate.yaml
# pod/tolerate created

kubectl get pod -o wide
# NAME         READY   STATUS    RESTARTS   AGE    IP        NODE
# no-tolerate  1/1     Running   0          1m     <none>    master
# tolerate     1/1     Running   0          15s    <none>    worker
```

```bash
# worker에 taint를 추가합니다.
# 이번에는 key만 존재하는 taint를 적용해 봅니다.
kubectl taint node worker badsector=:NoSchedule
# node/worker tainted

kubectl get node worker -oyaml | grep -A 7 taints
#  taints:
#  - effect: NoSchedule
#    key: project
#    value: A
#  - effect: NoSchedule
#    key: badsector
```

```yaml
# badsector.yaml
apiVersion: v1
kind: Pod
metadata:
  name: badsector
spec:
  containers:
  - name: nginx
    image: nginx
  tolerations:
  - key: "project"
    value: "A"
    operator: "Equal"
    effect: "NoSchedule"
  - key: "badsector"
    operator: "Exists"
```
 
```bash
kubectl apply -f badsector.yaml
# pod/badsector created

kubectl get pod -o wide
# NAME         READY   STATUS    RESTARTS   AGE    IP         NODE
# no-tolerate  1/1     Running   0          5m     <none>     master
# tolerate     1/1     Running   0          2m     <none>     worker
# badsector    1/1     Running   0          16s    <none>     worker
```

```bash
# project taint 제거
kubectl taint node worker project-
# badsector taint 제거
kubectl taint node worker badsector-
```

## 11.4 `Affinity & AntiAffinity`

### 11.4.1 `NodeAffinity`

```yaml
# node-affinity.yaml
apiVersion: v1
kind: Pod
metadata:
  name: node-affinity
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
```

```bash
kubectl apply -f node-affinity.yaml
# pod/node-affinity created

kubectl get pods node-affinity -o wide
# NAME           READY   STATUS    RESTARTS  AGE   IP          NODE   ..
# node-affinity  1/1     Running   0         19s   10.42.0.8   master ..
```

### 11.4.2 `PodAffinity`

```yaml
# pod-affinity.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pod-affinity
spec:
  selector:
    matchLabels:
      app: affinity
  replicas: 2
  template:
    metadata:
      labels:
        app: affinity
    spec:
      containers:
      - name: nginx
        image: nginx
      affinity:
        podAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - affinity
            topologyKey: "kubernetes.io/hostname"
```

```bash
kubectl apply -f pod-affinity.yaml
# deployment.apps/pod-affinity created

kubectl get pod -o wide
# NAME              READY  STATUS    RESTARTS  AGE   IP           NODE
# pod-affinity-xxx  1/1    Running   0         11m   10.42.0.165  worker
# pod-affinity-xxx  1/1    Running   0         11m   10.42.0.166  worker
```

### 11.4.3 `PodAntiAffinity`

```yaml
# pod-antiaffinity.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pod-antiaffinity
spec:
  selector:
    matchLabels:
      app: antiaffinity
  replicas: 2
  template:
    metadata:
      labels:
        app: antiaffinity
    spec:
      containers:
      - name: nginx
        image: nginx
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - antiaffinity
            topologyKey: "kubernetes.io/hostname"
```

```bash
kubectl apply -f pod-antiaffinity.yaml
# deployment.apps/pod-antiaffinity created

kubectl get pod -o wide
# NAME                 READY  STATUS    RESTARTS AGE  IP           NODE
# pod-antiaffinity-xxx 1/1    Running   0        10s  10.42.0.168  master
# pod-antiaffinity-xxx 1/1    Running   0        11s  10.42.0.167  worker
```

### 11.4.4 `PodAffinity`와 `PodAntiAffinity` 활용법

#### cache 서버 설정

```yaml
# redis-cache.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-cache
spec:
  selector:
    matchLabels:
      app: store
  replicas: 2
  template:
    metadata:
      labels:
        app: store
    spec:
      affinity:
        # cache 서버끼리 멀리 스케줄링
        # app=store 라벨을 가진 Pod끼리 멀리 스케줄링
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - store
            topologyKey: "kubernetes.io/hostname"
      containers:
      - name: redis-server
        image: redis
```

#### web 서버 설정

```yaml
# web-server.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-server
spec:
  selector:
    matchLabels:
      app: web-store
  replicas: 2
  template:
    metadata:
      labels:
        app: web-store
    spec:
      affinity:
        # web 서버끼리 멀리 스케줄링
        # app=web-store 라벨을 가진 Pod끼리 멀리 스케줄링
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - web-store
            topologyKey: "kubernetes.io/hostname"
        # web-cache 서버끼리 가까이 스케줄링 
        # app=store 라벨을 가진 Pod끼리 가까이 스케줄링
        podAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - store
            topologyKey: "kubernetes.io/hostname"
      containers:
      - name: web-app
        image: nginx
```

```bash
kubectl apply -f redis-cache.yaml
# deployment.app/redis-cache created

kubectl apply -f web-server.yaml
# deployment.app/web-server created

kubectl get pod -owide
# NAME             READY  STATUS    RESTARTS  AGE     IP            NODE
# redis-cache-xxx  1/1    Running   0         10s     10.42.0.151   master
# redis-cache-xxx  1/1    Running   0         10s     10.42.0.152   worker
# web-server-xxxx  1/1    Running   0         11s     10.42.0.153   master
# web-server-xxxx  1/1    Running   0         11s     10.42.0.154   worker
```

### Clean up

```bash
kubectl delete deploy --all
kubectl delete pod --all
```
