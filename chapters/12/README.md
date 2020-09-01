# 12. 클러스터 관리

## 12.1 리소스 관리

### 12.1.1 LimitRange

```bash
kubectl run mynginx --image nginx

kubectl get pod mynginx -oyaml | grep resources
# resources: {}
```

```yaml
# limit-range.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: limit-range
spec:
  limits:
  - default:
      cpu: 400m
      memory: 512Mi
    defaultRequest:
      cpu: 300m
      memory: 256Mi
    max:
      cpu: 600m
      memory: 600Mi
    min:
      cpu: 200m
      memory: 200Mi
    type: Container
```

```bash
kubectl apply -f limit-range.yaml
# limitrange/limit-range created

kubectl run nginx-lr --image nginx
# pod/nginx-lr created

kubectl get pod nginx-lr -oyaml | grep -A 6 resources
#    resources:
#      limits:
#        cpu: 400m
#        memory: 512Mi
#      requests:
#        cpu: 300m
#        memory: 256Mi
```

```yaml
# pod-exceed.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-exceed
spec:
  containers:
  - image: nginx
    name: nginx
    resources:
      limits:
        cpu: "700m"
        memory: "700Mi"
      requests:
        cpu: "300m"
        memory: "256Mi"
```

```bash
kubectl apply -f pod-exceed.yaml
# Error from server (Forbidden): error when creating "STDIN": pods 
# "pod-exceed" is forbidden: [maximum cpu usage per Container 
# is 600m, but limit is 700m, maximum memory usage per Container 
# is 600Mi, but limit is 700Mi]
```

### Clean up

```bash
kubectl delete limitrange limit-range
kubectl delete pod --all
```

### 12.1.2 ResourceQuota

```yaml
# res-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: res-quota
spec:
  hard:
    limits.cpu: 700m
    limits.memory: 800Mi
    requests.cpu: 500m
    requests.memory: 700Mi
```

```bash
# ResourceQuota 생성
kubectl apply -f res-quota.yaml
# resourcequota/res-quota created 

# Pod 생성 limit CPU 600m
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: rq-1
spec:
  containers:
  - image: nginx
    name: nginx
    resources:
      limits:
        cpu: "600m"
        memory: "600Mi"
      requests:
        cpu: "300m"
        memory: "300Mi"
EOF
# pod/rq-1 created
```

```bash
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: rq-2
spec:
  containers:
  - image: nginx
    name: nginx
    resources:
      limits:
        cpu: "600m"
        memory: "600Mi"
      requests:
        cpu: "300m"
        memory: "300Mi"
EOF
# Error from server (Forbidden): error when creating "STDIN": 
# pods "rq-2" is forbidden: exceeded quota: res-quota, 
# requested: limits.cpu=600m,limits.memory=600Mi,requests.cpu=300m, 
# used: limits.cpu=600m,limits.memory=600Mi,requests.cpu=300m, 
# limited: limits.cpu=700m,limits
```

### Clean up

```bash
kubectl delete resourcequota res-quota
kubectl delete pod --all
```

## 12.2 노드 관리

### 12.2.1 Cordon

```bash
# 먼저 worker의 상태를 확인합니다.
kubectl get node worker -oyaml | grep spec -A 5
# spec:
#   podCIDR: 10.42.0.0/24
#   podCIDRs:
#   - 10.42.0.0/24
#   providerID: k3s://worker
# status:

# worker를 cordon시킵니다.
kubectl cordon worker
# node/worker cordoned

# 다시 worker의 상태를 확인합니다. taint가 설정된 것을 확인할 수 있고 unschedulable이 true로 설정되어 있습니다.
kubectl get node worker -oyaml | grep spec -A 10
# spec:
#   podCIDR: 10.42.0.0/24
#   podCIDRs:
#   - 10.42.0.0/24
#   providerID: k3s://worker
#   taints:
#   - effect: NoSchedule
#     key: node.kubernetes.io/unschedulable
#     timeAdded: "2020-04-04T11:04:48Z"
#   unschedulable: true
# status:

# worker의 상태를 확인합니다.
kubectl get node
# NAME     STATUS                    ROLES    AGE   VERSION
# master   Ready                     master   32d   v1.18.6+k3s1
# worker   Ready,SchedulingDisabled  worker   32d   v1.18.6+k3s1
```

```bash
cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: rs
spec:
  replicas: 5
  selector:
    matchLabels:
      run: rs
  template:
    metadata:
      labels:
        run: rs
    spec:
      containers:
      - name: nginx
        image: nginx
EOF

kubectl get pod -o wide
# NAME     READY   STATUS    RESTARTS   AGE    IP          NODE     ...
# rs-xxxx  1/1     Running   0          3s     10.42.1.6   master   ...
# rs-xxxx  1/1     Running   0          3s     10.42.1.7   master   ...
# rs-xxxx  1/1     Running   0          3s     10.42.1.8   master   ...
# rs-xxxx  1/1     Running   0          3s     10.42.1.9   master   ...
# rs-xxxx  1/1     Running   0          3s     10.42.1.10  master   ...
```

```bash
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: pod-worker
spec:
  containers:
  - image: nginx
    name: nginx
  nodeSelector:
    kubernetes.io/hostname: worker
EOF
# pod/pod-worker created

kubectl get pod -owide
# NAME         READY  STATUS    RESTARTS   AGE     IP       NODE    ... 
# ...
# pod-worker   0/1    Pending   0          70s     <none>   <none>  ...
```

### 12.2.2 Uncordon

```bash
kubectl uncordon worker
# node/worker uncordoned

# taint가 사라졌습니다.
kubectl get node worker -oyaml | grep spec -A 10
# spec:
#   podCIDR: 10.42.1.0/24
#   podCIDRs:
#   - 10.42.1.0/24
#   providerID: k3s://worker
# status:
#   addresses:
#   - address: 172.31.16.173
#     type: InternalIP
#   - address: worker
#     type: Hostname

kubectl get node
# NAME     STATUS   ROLES    AGE   VERSION
# master   Ready    master   32d   v1.18.6+k3s1
# worker   Ready    worker   32d   v1.18.6+k3s1

kubectl get pod -owide
# NAME        READY   STATUS    RESTARTS   AGE   IP       NODE     ...
# ...
# pod-worker  1/1     Running   0          70s   <none>   worker   ...

kubectl delete pod pod-worker
# pod/pod-worker deleted
```

### 12.2.3 Drain

```bash
cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 3
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
EOF
# deployment.apps/pod-drain created

# nginx Pod가 워커 노드에 생성된 것을 확인할 수 있습니다.
kubectl get pod -o wide
# NAME               READY  STATUS    RESTARTS  AGE  IP           NODE
# nginx-7ff78b8-xxx  1/1    Running   0         42s  10.42.0.25   master
# nginx-7ff78b8-xxx  1/1    Running   0         42s  10.42.1.2    worker
# nginx-7ff78b8-xxx  1/1    Running   0         42s  10.42.4.62   worker
```

```bash
# 모든 노드에 존재하는 DaemonSet은 무시합니다.
kubectl drain worker  --ignore-daemonsets
# node/worker cordoned
# evicting pod "nginx-xxx"
# evicting pod "nginx-xxx"
# ...

# nginx Pod가 어떻게 동작하는지 확인합니다.
kubectl get pod -owide
# NAME              READY   STATUS    RESTARTS  AGE  IP          NODE
# nginx-7ff7b-xxx   1/1     Running   0         2m   10.42.0.25  master
# nginx-7ff7b-xxx   1/1     Pending   0         2m   <none>      <none>
 
kubectl get node worker -oyaml | grep spec -A 10
# spec:
#   podCIDR: 10.42.1.0/24
#   podCIDRs:
#   - 10.42.1.0/24
#   providerID: k3s://worker
#   taints:
#   - effect: NoSchedule
#     key: node.kubernetes.io/unschedulable
#     timeAdded: "2020-04-04T15:37:25Z"
#   unschedulable: true
# status:

kubectl get node
# NAME     STATUS                    ROLES    AGE   VERSION
# master   Ready                     master   32d   v1.18.6+k3s1
# worker   Ready,SchedulingDisabled  worker   32d   v1.18.6+k3s1
```

```bash
kubectl uncordon worker
# node/worker uncordoned
```

## 12.3 Pod 개수 유지

```bash
kubectl scale deploy nginx --replicas 10
# deployment.apps/mydeploy scaled
```

```yaml
# nginx-pdb.yaml
apiVersion: policy/v1beta1
kind: PodDisruptionBudget
metadata:
  name: nginx-pdb
spec:
  minAvailable: 9
  selector:
    matchLabels:
      app: nginx
```

```bash
# pdb를 생성합니다.
kubectl apply -f nginx-pdb.yaml
# poddisruptionbudget/nginx-pdb created

# worker을 drain합니다.
kubectl drain worker --ignore-daemonsets
# node/worker cordoned
# evicting pod "nginx-xxx"
# evicting pod "nginx-xxx"
# error when evicting pod "mynginx-xxx" 
# (will retry after 5s): Cannot evict pod as it would violate the 
#   pod's disruption budget.
# pod/mynginx-xxx evicted
# evicting pod "mynginx-xxx"
# error when evicting pod "mynginx-xxx" 
# (will retry after 5s): Cannot evict pod as it would violate the 
#   pod's disruption budget.
# evicting pod "mynginx-xxx"
# pod/mynginx-xxx evicted
# node/worker evicted
```

### Clean up

```bash
kubectl delete pdb nginx-pdb
kubectl delete deploy nginx
kubectl delete rs rs
kubectl uncordon worker
```
