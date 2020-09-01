# 10. 스토리지

## 10.1 `PersistentVolume`

### 10.1.1 hostPath PV

```yaml
# hostpath-pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-volume
spec:
  storageClassName: manual
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /tmp
```

```bash
kubectl apply -f hostpath-pv.yaml
# persistentvolume/my-volume created

kubectl get pv
# NAME        CAPACITY  ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   REASON   AGE
# my-volume   1Gi       RWO            Retain           Available           manual                  12s
```

### 10.1.2 NFS PV

```yaml
# my-nfs.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-nfs
spec:
  storageClassName: nfs
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteMany
  mountOptions:
    - hard
    - nfsvers=4.1
  nfs:
    path: /tmp
    server: <NFS_SERVER_IP>
```

### 10.1.3 awsElasticBlockStore PV

---

**![주의](warning.png) 주의** 

다음 예제는 AWS 플랫폼 위에서 적절한 권한이 부여된 환경에서만 동작합니다. 볼륨을 생성하여 `<volume-id>`를 입력해 주시기 바랍니다. (예제에서는 `vol-1234567890abcdef0`)

```bash
aws ec2 create-volume --availability-zone=eu-east-1a \
  --size=80 --volume-type=gp2
# {
#     "AvailabilityZone": "us-east-1a",
#     "Tags": [],
#     "Encrypted": false,
#     "VolumeType": "gp2",
#     "VolumeId": "vol-1234567890abcdef0",
#     "State": "creating",
#     "Iops": 240,
#     "SnapshotId": "",
#     "CreateTime": "YYYY-MM-DDTHH:MM:SS.000Z",
#     "Size": 80
# }
```

---

```yaml
# aws-ebs.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: aws-ebs
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  awsElasticBlockStore:
    volumeID: <volume-id>
    fsType: ext4
```

### 10.1.4 그외 다른 `PersistentVolume`

더 다양한 종류들을 확인하고 싶으시다면 다음 페이지를 참고 바랍니다. [https://kubernetes.io/docs/concepts/storage/volumes](https://kubernetes.io/docs/concepts/storage/volumes)

## 10.2 PersistentVolumeClaim

```yaml
# my-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

```bash
kubectl apply -f my-pvc.yaml
# persistentvolumeclaim/my-pvc created

# 앞에서 생성한 my-volume을 선점하였습니다.
kubectl get pvc
# NAME          STATUS   VOLUME      CAPACITY  ACCESS MODES    ... 
# my-pvc        Bound    my-volume   1Gi       RWO             ...

kubectl get pv
# NAME        CAPACITY  ACCESS MODES   RECLAIM POLICY   STATUS   
# my-volume   1Gi       RWO            Retain           Bound    
#
#                 CLAIM              STORAGECLASS    REASON   AGE
#                 default/my-pvc     manual                   11s
```

```yaml
# use-pvc.yaml
apiVersion: v1
kind: Pod
metadata:
  name: use-pvc
spec:
  containers: 
  - name: nginx
    image: nginx
    volumeMounts:
    - mountPath: /test-volume
      name: vol
  volumes:
  - name: vol
    persistentVolumeClaim:
      claimName: my-pvc
```

```bash
kubectl apply -f use-pvc.yaml
# pod/use-pvc created

# 데이터 저장
kubectl exec use-pvc -- sh -c "echo 'hello' > /test-volume/hello.txt"
```

```bash
kubectl delete pod use-pvc
# pod/use-pvc deleted

kubectl apply -f use-pvc.yaml
# pod/use-pvc created

kubectl exec use-pvc -- cat /test-volume/hello.txt
# hello
```

### Clean up

```bash
kubectl delete pod use-pvc
kubectl delete pvc my-pvc
kubectl delete pv my-volume
```

## 10.3 `StorageClass`

### 10.3.1 `StorageClass` 소개

- local-path: [https://github.com/rancher/local-path-provisioner](https://github.com/rancher/local-path-provisioner)

```bash
# local-path라는 이름의 StorageClass
kubectl get sc
# NAME                  PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
# local-path (default)  rancher.io/local-path   Delete          WaitForFirstConsumer   false                  20d

kubectl get sc local-path -oyaml
# apiVersion: storage.k8s.io/v1
# kind: StorageClass
# metadata:
#   annotations:
#     objectset.rio.cattle.io/id: ""
#   ...
#   name: local-path
#   resourceVersion: "172"
#   selfLink: /apis/storage.k8s.io/v1/storageclasses/local-path
#   uid: 3aede349-0b94-40c8-b10a-784d38f7c120
# provisioner: rancher.io/local-path
# reclaimPolicy: Delete
# volumeBindingMode: WaitForFirstConsumer
```

```yaml
# my-pvc-sc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc-sc
spec:
  storageClassName: local-path
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

```bash
kubectl apply -f my-pvc-sc.yaml
# persistentvolumeclaim/my-pvc-sc created

kubectl get pvc my-pvc-sc
# NAME         STATUS    VOLUME     CAPACITY   ACCESS MODES  STORAGECLASS   AGE 
# my-pvc-sc    Pending                                       local-path     11s 
```

```yaml
# use-pvc-sc.yaml
apiVersion: v1
kind: Pod
metadata:
  name: use-pvc-sc
spec:
  volumes:
  - name: vol
    persistentVolumeClaim:
      claimName: my-pvc-sc
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - mountPath: "/usr/share/nginx/html"
      name: vol
```

```bash
# pod 생성
kubectl apply -f use-pvc-sc.yaml
# pod/use-pvc-sc created

# STATUS가 Bound로 변경
kubectl get pvc my-pvc-sc
# NAME         STATUS   VOLUME            CAPACITY   ACCESS MODES   STORAGECLASS   AGE
# my-pvc-sc    Bound    pvc-479cff32-xx   1Gi        RWO            local-path     92s         

# 기존에 생성하지 않은 신규 volume이 생성된 것을 확인
kubectl get pv
# NAME              CAPACITY  ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM               STORAGECLASS   REASON   AGE
# pvc-479cff32-xx   1Gi       RWO            Delete           Bound    default/my-pvc-sc   local-path              3m

# pv 상세 정보 확인 (hostPath 등)
kubectl get pv pvc-479cff32-xx -oyaml
# apiVersion: v1
# kind: PersistentVolume
# metadata:
#     ...
#   name: pvc-b1727544-f4be-4cd6-acb7-29eb8f68e84a
#   ...
# spec:
#   ...
#   hostPath:
#     path: /var/lib/rancher/k3s/storage/pvc-b1727544-f4be-4cd6-acb7-29eb8f68e84a
#     type: DirectoryOrCreate
#   nodeAffinity:
#     required:
#       nodeSelectorTerms:
#       - matchExpressions:
#         - key: kubernetes.io/hostname
#           operator: In
#           values:
#           - worker
#    ...
```

### 10.3.2 NFS StorageClass 설정

```bash
helm install nfs stable/nfs-server-provisioner \
    --set persistence.enabled=true \
    --set persistence.size=10Gi \
    --version 1.1.1 \
    --namespace ctrl
# NAME: nfs
# LAST DEPLOYED: Wed Jul  8 13:19:46 2020
# NAMESPACE: ctrl
# STATUS: deployed
# REVISION: 1
# TEST SUITE: None
# NOTES:
# ...

# nfs-server-provisioner라는 Pod가 생성되어 있습니다.
kubectl get pod -n ctrl
# NAME                           READY   STATUS       RESTARTS   AGE
# ...
# nfs-nfs-server-provisioner-0   1/1     Running      0          4m

# 이것은 StatefulSet로 구성되어 있습니다.
kubectl get statefulset  -n ctrl
# NAME                         READY   AGE
# nfs-nfs-server-provisioner   1/1     57s

# nfs-server-provisioner Service도 있습니다.
kubectl get svc  -n ctrl
# NAME                                  TYPE           CLUSTER-IP     ..
# nginx-nginx-ingress-default-backend   ClusterIP      10.43.79.133   .. 
# nginx-nginx-ingress-controller        LoadBalancer   10.43.182.174  ..  
# nfs-nfs-server-provisioner            ClusterIP      10.43.248.122  ..  

# 새로운 nfs StorageClass 생성
kubectl get sc
# NAME                 PROVISIONER                                RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
# local-path (default) rancher.io/local-path                      Delete          WaitForFirstConsumer   false                  20d
# nfs                  cluster.local/nfs-nfs-server-provisioner   Delete          Immediate              true                   10s
```

```yaml
# nfs-sc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nfs-sc
spec:
  # 기존 local-path에서 nfs로 변경
  storageClassName: nfs
  # accessModes를 ReadWriteMany로 변경
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
```

```bash
kubectl apply -f nfs-sc.yaml
# persistentvolumeclaim/nfs-sc created

# pvc 리소스 확인
kubectl get pvc
# NAME        STATUS   VOLUME             CAPACITY   ACCESS MODES  ...
# my-pvc-sc   Bound    pvc-b1727544-xxx   1Gi        RWO           ...
# nfs-sc      Bound    pvc-49fea9cf-xxx   1Gi        RWO           ...

# pv 리소스 확인
kubectl get pv pvc-49fea9cf-xxx
# NAME                CAPACITY   ACCESS MODES   RECLAIM  POLICY  STATUS    CLAIM            STORAGECLASS   REASON  AGE
# pvc-49fea9cf-xxx    1Gi        RWX            Delete           Bound     default/nfs-sc   nfs                    5m

# pv 상세 정보 확인 (nfs 마운트 정보)
kubectl get pv pvc-49fea9cf-xxx -oyaml
# apiVersion: v1
# kind: PersistentVolume
# metadata:
#   ...
# spec:
#   accessModes:
#   - ReadWriteMany
#   capacity:
#     storage: 1Gi
#   claimRef:
#     apiVersion: v1
#     kind: PersistentVolumeClaim
#     name: nfs-sc
#     namespace: default
#     resourceVersion: "10084380"
#     uid: 2e95f6c4-2b43-4375-808f-0c93e44a1003
#   mountOptions:
#   - vers=3
#   nfs:
#     path: /export/pvc-2e95f6c4-2b43-4375-808f-0c93e44a1003
#     server: 10.43.248.122
#   persistentVolumeReclaimPolicy: Delete
#   storageClassName: nfs
#   volumeMode: Filesystem
# status:
#   phase: Bound
```

```yaml
# use-nfs-sc.yaml
apiVersion: v1
kind: Pod
metadata:
  name: use-nfs-sc-master
spec:
  volumes:
  - name: vol
    persistentVolumeClaim:
      claimName: nfs-sc
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - mountPath: "/usr/share/nginx/html"
      name: vol
  nodeSelector:
    kubernetes.io/hostname: master
---
apiVersion: v1
kind: Pod
metadata:
  name: use-nfs-sc-worker
spec:
  volumes:
  - name: vol
    persistentVolumeClaim:
      claimName: nfs-sc
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - mountPath: "/usr/share/nginx/html"
      name: vol
  nodeSelector:
    kubernetes.io/hostname: worker
```

```bash
kubectl apply -f use-nfs-sc.yaml
# pod/use-nfs-sc-master created
# pod/use-nfs-sc-worker created

kubectl get pod -o wide
# NAME               READY  STATUS    RESTARTS  AGE   IP          NODE
# ...
# use-nfs-sc-master  1/1    Running   0         19s   10.42.0.8   master
# use-nfs-sc-worker  1/1    Running   0         19s   10.42.0.52  worker
```

```bash
# master Pod에 index.html 파일을 생성합니다.
kubectl exec use-nfs-sc-master -- sh -c \
      "echo 'hello world' >> /usr/share/nginx/html/index.html"

# worker Pod에서 호출을 합니다.
kubectl exec use-nfs-sc-worker -- curl -s localhost
# hello world
```

### Clean up

```bash
kubectl delete pod user-nfs-sc-master
kubectl delete pod user-nfs-sc-worker
kubectl delete pvc nfs-sc
```

## 10.4 쿠버네티스 스토리지 활용

```bash
# stable 레포지토리에 있는 minio chart를 다운로드 합니다.
helm fetch --untar stable/minio --version 5.0.30

# vim 편집기를 실행합니다.
vim minio/values.yaml
```

```yaml
...
# 약 65번째 줄에서 accessKey와 secretKey 변경
accessKey: "myaccess"
secretKey: "mysecret"
...
  # 약 111번째 줄에서 storageClass를 nfs로 변경
  storageClass: "nfs"
  # ReadWriteMany로 변경
  accessMode: "ReadWriteMany"
  # 2Gi로 변경
  size: 2Gi    # 기존 500Gi

# 약 149번째 줄에서 ingress 설정
ingress:
  # false --> true
  enabled: true
  labels: {}

  # annotation 설정
  annotations:
    kubernetes.io/ingress.class: nginx
  path: /
  # host 설정, 사용자별 공인IP 주소를 입력합니다.
  hosts:
    - minio.10.0.1.1.sslip.io
  tls: []

# 약 212번째 줄에서 requests 줄이기
resources:
  requests:
    memory: 1Gi # 기존 4Gi
```

```bash
helm install minio ./minio

kubectl get pod
# NAME                      READY   STATUS             RESTARTS   AGE
# minio-7f58448457-vctrp    1/1     Running            0          2m

kubectl get pvc
# NAME     STATUS   VOLUME             CAPACITY   ACCESS MODES   STORAGECLASS   AGE
# minio    Bound    pvc-cff81820-xxx   10Gi       RWO            nfs            2m40s

kubectl get pv
# NAME               CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM           STORAGECLASS   REASON   AGE   
# pvc-cff81820-xxx   10Gi       RWO            Delete           Bound    default/minio   nfs                     3m
```

### Clean up

```bash
helm delete minio
```
