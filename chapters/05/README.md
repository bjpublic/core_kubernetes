# 5. Pod 살펴보기

## 5.1 `Pod` 소개

```bash
# mynginx.yaml 이라는 YAML 정의서 생성
kubectl run mynginx --image nginx --dry-run=client -o yaml > mynginx.yaml

vim mynginx.yaml
```

```yaml
# mynginx.yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: mynginx
  name: mynginx
spec:
  containers:
  - image: nginx
    name: mynginx
  restartPolicy: Never
```

```bash
kubectl apply -f mynginx.yaml
# pod/mynginx created
```

`Pod`를 생성하면 다음과 같은 순서로 `Pod`가 실행됩니다.

## 5.2 라벨링 시스템


### 5.2.1 라벨 정보 부여

#### `label` 명령을 이용하는 방법

```bash
kubectl label pod mynginx hello=world
# pod/mynginx labeled
```

```bash
kubectl get pod mynginx -oyaml
# apiVersion: v1
# kind: Pod
# metadata:
#   creationTimestamp: "2020-06-21T06:54:52Z"
#   labels:
#     hello: world
#     run: mynginx
#   ...
```

#### 선언형 명령을 이용하는 방법

```bash
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  # hello=world 라벨 지정
  labels:
    hello: world  
    run: mynginx
  name: mynginx
spec:
  containers:
  - image: nginx
    name: mynginx
EOF
```

### 5.2.2 라벨 정보 확인

```bash
# 키 run에 대한 값 표시
kubectl get pod mynginx -L run
# NAME      READY   STATUS    RESTARTS   AGE   RUN
# mynginx   1/1     Running   0          15m   mynginx
```

```bash
# 모든 라벨 정보 표시
kubectl get pod mynginx --show-labels
# NAME      READY   STATUS    RESTARTS   AGE   LABELS
# mynginx   1/1     Running   0          83s   hello=world,run=mynginx
```

### 5.2.3 라벨을 이용한 조건 필터링

```bash
# 새로운 yournginx Pod 생성
kubectl run yournginx --image nginx
# pod/yournginx created

# key가 run인 Pod들 출력
kubectl get pod -l run
# NAME       READY   STATUS    RESTARTS   AGE
# mynginx    1/1     Running   0          19m
# yournginx  1/1     Running   0          20m

# key가 run이고 value가 mynginx인 Pod 출력
kubectl get pod -l run=mynginx
# NAME      READY   STATUS    RESTARTS   AGE
# mynginx   1/1     Running   0          19m

# key가 run이고 value가 yournginx Pod 출력
kubectl get pod -l run=yournginx
# NAME       READY   STATUS    RESTARTS   AGE
# yournginx  1/1     Running   0          20m
```

### 5.2.4 `nodeSelector`를 이용한 노드 선택

```bash
kubectl get node  --show-labels
# NAME     STATUS   ROLES    AGE   VERSION        LABELS
# master   Ready    master   14d   v1.18.6+k3s1   beta.kubernetes.io/...
# worker   Ready    <none>   14d   v1.18.6+k3s1   beta.kubernetes.io/...
```

```bash
kubectl label node master disktype=ssd
# node/master labeled

kubectl label node worker disktype=hdd
# node/worker labeled
```

```bash
# disktype 라벨 확인
kubectl get node --show-labels | grep disktype
# NAME     STATUS   ROLES    AGE   VERSION        LABELS
# master   Ready    master   14d   v1.18.6+k3s1   ....disktype=ssd,....
# worker   Ready    <none>   14d   v1.18.6+k3s1   ....disktype=hdd,....
```

```yaml
# node-selector.yaml
apiVersion: v1
kind: Pod
metadata:
  name: node-selector
spec:
  containers: 
  - name: nginx
    image: nginx
  # 특정 노드 라벨 선택
  nodeSelector:
    disktype: ssd
```

```bash
kubectl apply -f node-selector.yaml
# pod/node-selector created
```

```bash
kubectl get pod node-selector -o wide
# NAME           READY   STATUS    RESTARTS   AGE   IP          NODE   
# node-selector  1/1     Running   0          19s   10.42.0.8   master
```

```yaml
# node-selector.yaml
apiVersion: v1
kind: Pod
metadata:
  name: node-selector
spec:
  containers: 
  - name: nginx
    image: nginx
  # 특정 노드 라벨 선택
  nodeSelector:
    disktype: hdd     # 기존 ssd에서 hdd로 변경
```

```bash
# 기존의 Pod 삭제
kubectl delete pod node-selector
# pod/node-selector deleted

# 새로 라벨링한 Pod 생성
kubectl apply -f node-selector.yaml
# pod/node-selector created

kubectl get pod node-selector -o wide
# NAME            READY   STATUS    RESTARTS   AGE   IP          NODE  
# node-selector   1/1     Running   0          19s   10.42.0.6   worker 
```

## 5.3 실행명령 및 파라미터 지정

```yaml
# cmd.yaml
apiVersion: v1
kind: Pod
metadata:
  name: cmd
spec:
  restartPolicy: OnFailure
  containers: 
  - name: nginx
    image: nginx
    # 실행명령
    command: ["/bin/echo"]
    # 파라미터
    args: ["hello"]
```

```bash
kubectl apply -f cmd.yaml
# pod/cmd created

kubectl logs -f cmd
# hello
```

## 5.4 환경변수 설정

```yaml
# env.yaml
apiVersion: v1
kind: Pod
metadata:
  name: env
spec:
  containers: 
  - name: nginx
    image: nginx
    env:
    - name: hello
      value: "world!"
```

```bash
# env.yaml 파일을 이용하여 Pod 생성
kubectl apply -f env.yaml
#pod/env created

# 환경변수 hello 확인
kubectl exec env -- printenv | grep hello
# hello=world!
```

## 5.5 `Volume` 연결

```yaml
# volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: volume
spec:
  containers: 
  - name: nginx
    image: nginx

    # 컨테이너 내부의 연결 위치 지정
    volumeMounts:
    - mountPath: /container-volume
      name: my-volume
  
  # host 서버의 연결 위치 지정
  volumes:
  - name: my-volume
    hostPath:
      path: /home
```

```bash
kubectl apply -f volume.yaml
# pod/volume created

kubectl exec volume -- ls /container-volume
# ubuntu

ls /home
# ubuntu
```

```yaml
# volume-empty.yaml
apiVersion: v1
kind: Pod
metadata:
  name: volume-empty
  labels:
    name: volume-empty
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts: # 컨테이너 내부의 연결 위치 지정
    - name: shared-storage
      mountPath: /container-volume
  - name: redis
    image: redis
    volumeMounts:
    - name: shared-storage
      mountPath: /container-volume
  volumes: 
  - name: shared-storage
    emptyDir: {}
```

```bash
# pod 내부의 컨테이너간 공유 디렉토리 pod 생성
$ kubectl apply -f volume-empty.yaml
# pod/volume-empty created

# pod 내부의 각각의 컨테이너에 접근하기
$ kubectl exec -it volume-empty --container nginx -- bash
# root@volume-empty:/$ cd /container-volume/
# root@volume-empty:/container-volume$ touch volume.txt
# root@volume-empty:/container-volume# ls -al
# total 8
# drwxrwxrwx 2 root root 4096 Oct 22 09:59 .
# drwxr-xr-x 1 root root 4096 Oct 22 09:55 ..
# -rw-r--r-- 1 root root    0 Oct 22 09:59 volume.txt

# 다른 컨테이너에서 내용 확인
$ kubectl exec -it volume-empty --container redis -- bash
# root@volume-empty:/data# ls -al /container-volume/
# total 8
# drwxrwxrwx 2 root root 4096 Oct 22 09:59 .
# drwxr-xr-x 1 root root 4096 Oct 22 09:55 ..
# -rw-r--r-- 1 root root    0 Oct 22 09:59 volume.txt
```

## 5.6 리소스 관리

### 5.6.1 requests

```yaml
# requests.yaml
apiVersion: v1
kind: Pod
metadata:
  name: requests
spec:
  containers: 
  - name: nginx
    image: nginx
    resources:
      requests:
        cpu: "250m"
        memory: "500Mi"
```

### 5.6.2 limits

```yaml
# limits.yaml
apiVersion: v1
kind: Pod
metadata:
  name: limits
spec:
  restartPolicy: OnFailure
  containers: 
  - name: mynginx
    image: python:3.7
    command: [ "python" ]
    args: [ "-c", "arr = []\nwhile True: arr.append(range(1000))" ]
    resources:
      limits:
        cpu: "500m"
        memory: "1Gi"
```

```bash
kubectl apply -f limits.yaml
# pod/limits created

watch kubectl get pod limits
# NAME    READY   STATUS     RESTARTS   AGE
# limits  1/1     Running    0          1m
# ...
# limits  0/1     OOMKilled  1          1m
```

```yaml
# resources.yaml
apiVersion: v1
kind: Pod
metadata:
  name: resources
spec:
  containers: 
  - name: nginx
    image: nginx
    resources:
      requests:
        cpu: "250m"
        memory: "500Mi"
      limits:
        cpu: "500m"
        memory: "1Gi"
```

## 5.7 상태 확인

### 5.7.1 `livenessProbe`

```yaml
# liveness.yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness
spec:
  containers: 
  - name: nginx
    image: nginx
    livenessProbe:
      httpGet:
        path: /live
        port: 80
```

```bash
kubectl apply -f liveness.yaml
# pod/liveness created

# <CTRL> + <C>로 watch를 종료할 수 있습니다.
watch kubectl get pod liveness
# NAME       READY   STATUS    RESTARTS   AGE
# liveness   1/1     Running   2          71s

# 기본적으로 nginx에는 /live 라는 API가 없습니다.
kubectl logs -f liveness
# ...
# 10.42.0.1 - - [13/Aug/2020:12:31:24 +0000] "GET /live HTTP/1.1" 404 153 "-" "kube-probe/1.18" "-"
# 10.42.0.1 - - [13/Aug/2020:12:31:34 +0000] "GET /live HTTP/1.1" 404 153 "-" "kube-probe/1.18" "-"
```

```bash
kubectl exec liveness -- touch /usr/share/nginx/html/live

kubectl logs liveness
# 10.42.0.1 - - [14/Aug/2020:08:50:08 +0000] "GET /live HTTP/1.1" 404 153 "-" "kube-probe/1.18" "-"
# 10.42.0.1 - - [14/Aug/2020:08:50:18 +0000] "GET /live HTTP/1.1" 200 0 "-" "kube-probe/1.18" "-"

kubectl get pod liveness
# NAME       READY   STATUS      RESTARTS   AGE
# liveness   1/1     Running     2          12m
``` 

### 5.7.2 `readinessProbe`

```yaml
# readiness.yaml
apiVersion: v1
kind: Pod
metadata:
  name: readiness
spec:
  containers: 
  - name: nginx
    image: nginx
    readinessProbe:
      httpGet:
        path: /ready
        port: 80
```

```bash
kubectl apply -f readiness.yaml
# pod/readiness created

kubectl logs -f readiness
# 10.42.0.1 - - [28/Jun/2020:13:31:28 +0000] "GET /ready HTTP/1.1" 
# 404 153 "-" "kube-probe/1.18" "-"

# 기본적으로 nginx에는 /ready 라는 API가 없습니다.
# /ready 호출에 404 에러가 반환되어 준비 상태가 완료되지 않습니다.
kubectl get pod
# NAME        READY   STATUS      RESTARTS   AGE
# readiness   0/1     Running     0          2m

# /ready URL 생성
kubectl exec readiness -- touch /usr/share/nginx/html/ready

# READY 1/1로 준비 완료 상태로 변경되었습니다.
kubectl get pod
# NAME        READY   STATUS      RESTARTS   AGE
# readiness   1/1     Running     0          2m
```

```yaml
# readiness-cmd.yaml
apiVersion: v1
kind: Pod
metadata:
  name: readiness-cmd
spec:
  containers: 
  - name: nginx
    image: nginx
    readinessProbe:
      exec:
        command:
        - cat
        - /tmp/ready
```

```bash
kubectl apply -f readiness-cmd.yaml
# pod/readiness-cmd created

# /tmp/ready 라는 파일이 존재하지 않기 때문에
# READY 0/1로 준비가 완료 되지 않음
kubectl get pod
# NAME            READY   STATUS      RESTARTS   AGE
# readiness-cmd   0/1     Running     0          2m

# /tmp/ready 파일 생성
kubectl exec readiness-cmd -- touch /tmp/ready

# READY 1/1로 준비 완료 상태로 변경
kubectl get pod
# NAME            READY   STATUS      RESTARTS   AGE
# readiness-cmd   1/1     Running     0          2m
```

## 5.8 두 개 컨테이너 실행

```yaml
# second.yaml
apiVersion: v1
kind: Pod
metadata:
  name: second
spec:
  containers: 
  - name: nginx
    image: nginx
  - name: curl
    image: curlimages/curl
    command: ["/bin/sh"]
    args: ["-c", "while true; do sleep 5; curl -s localhost; done"]
```

```bash
kubectl apply -f second.yaml
# pod/second created

kubectl logs second
# error: a container name must be specified for pod second, choose one of: [nginx curl]
```

```bash
# nginx 컨테이너 지정
kubectl logs second -c nginx
# 127.0.0.1 - - [22/Jun/2020:13:37:00 +0000] "GET / HTTP/1.1" 200 
# 612 "-" "curl/7.70.0-DEV" "-"
# 127.0.0.1 - - [22/Jun/2020:13:37:09 +0000] "GET / HTTP/1.1" 200 
# 612 "-" "curl/7.70.0-DEV" "-"

# curl 컨테이너 지정
kubectl logs second -c curl
# ...
```

## 5.9 초기화 컨테이너

```yaml
# init-container.yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-container
spec:
  restartPolicy: OnFailure
  containers: 
  - name: busybox
    image: k8s.gcr.io/busybox
    command: [ "ls" ]
    args: [ "/tmp/moby" ]
    volumeMounts:
    - name: workdir
      mountPath: /tmp
  initContainers:
  - name: git
    image: alpine/git
    command: ["sh"]
    args:
    - "-c"
    - "git clone https://github.com/moby/moby.git /tmp/moby"
    volumeMounts:
    - name: workdir
      mountPath: "/tmp"
  volumes:
  - name: workdir
    emptyDir: {}
```

```bash
kubectl apply -f init-container.yaml
# pod/init-container created

watch kubectl get pod
# NAME            READY   STATUS      RESTARTS   AGE
# init-container  0/1     Init:0/1    0          2s

# initContainer log 확인
kubectl logs init-container -c git -f
# Cloning into '/tmp/moby'...

# 메인 컨테이너 (busybox) log 확인
kubectl logs init-container
# AUTHORS
# CHANGELOG.md
# CONTRIBUTING.md
# Dockerfile
# Dockerfile.buildx
# ...
```

## 5.10 Config 설정

### 5.10.1 ConfigMap 리소스 생성

```properties
# game.properties
weapon=gun
health=3
potion=5
```

```bash
kubectl create configmap game-config --from-file=game.properties
# configmap/game-config created
```

```bash
kubectl get configmap game-config -o yaml  # 축약하여 cm
# apiVersion: v1
# data:
#   game.properties: |
#     weapon=gun
#     health=3
#     potion=5
# kind: ConfigMap
# metadata:
#   name: game-config
#   namespace: default
```

```bash
kubectl create configmap special-config \
            --from-literal=special.power=10 \
            --from-literal=special.strength=20
# configmap/special-config created
```

```bash
kubectl get cm special-config -o yaml
# apiVersion: v1
# kind: ConfigMap
# metadata:
#   name: special-config
#   namespace: default
# data:
#   special.power: 10
#   special.strength: 20
```

```yaml
# monster-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: monster-config
  namespace: default
data:
  monsterType: fire
  monsterNum: "5"
  monsterLife: "3"
```

```bash
kubectl apply -f monster-config.yaml
# configmap/monster-config created

kubectl get cm monster-config -o yaml
# apiVersion: v1
# kind: ConfigMap
# metadata:
#   name: monster-config
#   namespace: default
# data:
#   monsterType: fire
#   monsterNum: "5"
#   monsterLife: "3"
```

### 5.10.2 ConfigMap 활용

#### 볼륨 연결

```yaml
# game-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: game-volume
spec:
  restartPolicy: OnFailure
  containers:
  - name: game-volume
    image: k8s.gcr.io/busybox
    command: [ "/bin/sh", "-c", "cat /etc/config/game.properties" ]
    volumeMounts:
    - name: game-volume
      mountPath: /etc/config
  volumes:
  - name: game-volume
    configMap:
      name: game-config
```

```bash
kubectl apply -f game-volume.yaml
# pod/game-volume created

# 로그를 확인합니다.
kubectl logs game-volume
# weapon=gun
# health=3
# potion=5
```

#### 환경변수 - valueFrom

```yaml
# special-env.yaml
apiVersion: v1
kind: Pod
metadata:
  name: special-env
spec:
  restartPolicy: OnFailure
  containers:
  - name: special-env
    image: k8s.gcr.io/busybox
    command: [ "printenv" ]
    args: [ "special_env" ]
    env:
    - name: special_env
      valueFrom:
        configMapKeyRef:
          name: special-config
          key: special.power
```

```bash
kubectl apply -f special-env.yaml
# pod/special-env created

kubectl logs special-env
# 10
```

#### 환경변수 - envFrom

```yaml
# monster-env.yaml
apiVersion: v1
kind: Pod
metadata:
  name: monster-env
spec:
  restartPolicy: OnFailure
  containers:
  - name: monster-env
    image: k8s.gcr.io/busybox
    command: [ "printenv" ]
    # env 대신에 envFrom 사용
    envFrom:
    - configMapRef:
        name: monster-config
```

```bash
kubectl apply -f monster-env.yaml
# pod/monster-env created

kubectl logs monster-env | grep monster
# HOSTNAME=monster-env
# monsterLife=3
# monsterNum=5
# monsterType=fire
```

## 5.11 민감 데이터 관리

### 5.11.1 Secret 리소스 생성

```bash
echo -ne admin | base64
# YWRtaW4=

echo -ne password123 | base64
# cGFzc3dvcmQxMjM=
```

```yaml
# user-info.yaml
apiVersion: v1
kind: Secret
metadata:
  name: user-info
type: Opaque
data:
  username: YWRtaW4=            # admin
  password: cGFzc3dvcmQxMjM=    # password123
```

```bash
kubectl apply -f user-info.yaml
# secret/user-info created

kubectl get secret user-info -o yaml
# apiVersion: v1
# data:
#   password: cGFzc3dvcmQxMjM=
#   username: YWRtaW4=
# kind: Secret
# metadata:
#   ...
#   name: user-info
#   namespace: default
#   resourceVersion: "6386"
#   selfLink: /api/v1/namespaces/default/secrets/user-info
#   uid: bd6ca3a6-17f1-4690-aefe-6200e402aa35
# type: Opaque
```

```yaml
# user-info-stringdata.yaml
apiVersion: v1
kind: Secret
metadata:
  name: user-info-stringdata
type: Opaque
stringData:
  username: admin
  password: password123
```

```bash
kubectl apply -f user-info-stringdata.yaml
# secret/user-info created

kubectl get secret user-info-stringdata -o yaml
# apiVersion: v1
# data:
#   password: cGFzc3dvcmQxMjM=
#   username: YWRtaW4=
# kind: Secret
# metadata:
#   ...
#   name: user-info-stringdata
#   namespace: default
#   resourceVersion: "6386"
#   selfLink: /api/v1/namespaces/default/secrets/user-info
#   uid: bd61b459-a0d4-4158-aefe-6200f202aa35
# type: Opaque
```

```bash
# user-info.properties
username=admin
password=password123
```

```bash
kubectl create secret generic user-info-from-file \
                    --from-env-file=user-info.properties
# secret/user-info-from-file created

kubectl get secret user-info-from-file -oyaml
# apiVersion: v1
# data:
#   password: cGFzc3dvcmQxMjM=
#   username: YWRtaW4=
# kind: Secret
# metadata:
#   creationTimestamp: "2020-07-07T12:03:14Z"
#   name: user-info-from-file
#   namespace: default
#   resourceVersion: "3647019"
#   selfLink: /api/v1/namespaces/default/secrets/user-info-from-file2
#   uid: 57bc52e1-4158-4f13-a0d4-0581b45950db
# type: Opaque
```

### 5.11.2 Secret 활용

#### 볼륨 연결

```yaml
# secret-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-volume
spec:
  restartPolicy: OnFailure
  containers:
  - name: secret-volume
    image: k8s.gcr.io/busybox
    command: [ "sh" ]
    args: ["-c", "ls /secret; cat /secret/username"]
    volumeMounts:
    - name: secret
      mountPath: "/secret"
  volumes:
  - name: secret
    secret:
      secretName: user-info
```

```bash
kubectl apply -f secret-volume.yaml
# pod/secret-volume created

kubectl logs secret-volume
# password
# username
# admin
```

#### 환경변수 - env

```yaml
# secret-env.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-env
spec:
  restartPolicy: OnFailure
  containers:
  - name: secret-env
    image: k8s.gcr.io/busybox
    command: [ "printenv" ]
    env:
    - name: USERNAME
      valueFrom:
        secretKeyRef:
          name: user-info
          key: username
    - name: PASSWORD
      valueFrom:
        secretKeyRef:
          name: user-info
          key: password
```

```bash
kubectl apply -f secret-env.yaml
# pod/secret-env created

kubectl logs secret-env
# PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
# HOSTNAME=secret-envfrom
# USERNAME=admin
# PASSWORD=1f2d1e2e67df
# ...
```

#### 환경변수 - envFrom

```yaml
# secret-envfrom.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-envfrom
spec:
  restartPolicy: OnFailure
  containers:
  - name: secret-envfrom
    image: k8s.gcr.io/busybox
    command: [ "printenv" ]
    envFrom:
    - secretRef:
        name: user-info
```

```bash
kubectl apply -f secret-envfrom.yaml
# pod/secret-envfrom created

kubectl logs secret-envfrom
# PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
# HOSTNAME=secret-envfrom
# username=admin
# password=1f2d1e2e67df
# ...
```

## 5.12 메타데이터 전달

### 5.12.1 Volume 연결

```yaml
# downward-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: downward-volume
  labels:
    zone: ap-north-east
    cluster: cluster1
spec:
  restartPolicy: OnFailure
  containers:
  - name: downward
    image: k8s.gcr.io/busybox
    command: ["sh", "-c"]
    args: ["cat /etc/podinfo/labels"]
    volumeMounts:
    - name: podinfo
      mountPath: /etc/podinfo
  volumes:
  - name: podinfo
    downwardAPI:
      items:
      - path: "labels"
        fieldRef:
          fieldPath: metadata.labels
```

```bash
kubectl apply -f downward-volume.yaml
# pod/downward-volume created

# Pod의 라벨 정보와 비교해 보시기 바랍니다.
kubectl logs downward-volume
# cluster="cluster1"
# zone="ap-north-east"
```

### 5.12.2 환경변수 - env

```yaml
# downward-env.yaml
apiVersion: v1
kind: Pod
metadata:
  name: downward-env
spec:
  restartPolicy: OnFailure
  containers:
  - name: downward
    image: k8s.gcr.io/busybox
    command: [ "printenv"]
    env:
    - name: NODE_NAME
      valueFrom:
        fieldRef:
          fieldPath: spec.nodeName
    - name: POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: metadata.name
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          fieldPath: metadata.namespace
    - name: POD_IP
      valueFrom:
        fieldRef:
          fieldPath: status.podIP
```

```bash
kubectl apply -f downward-env.yaml
# pod/downward-env created

kubectl logs downward-env
# POD_NAME=downward-env
# POD_NAMESPACE=default
# POD_IP=10.42.0.219
# NODE_NAME=master
# ...
```

### Clean up

```bash
kubectl delete pod --all
```
