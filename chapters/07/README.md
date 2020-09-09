# 7. 쿠버네티스 컨트롤러

## 7.1 컨트롤러란?

컨트롤러에 대한 더 자세한 내용은 다음 페이지를 참고해 주시기 바랍니다.

[https://kubernetes.io/docs/concepts/architecture/controller](https://kubernetes.io/docs/concepts/architecture/controller)

## 7.2 ReplicaSet

```yaml
# myreplicaset.yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: myreplicaset
spec:
  replicas: 2
  selector:
    matchLabels:
      run: nginx-rs
  template:
    metadata:
      labels:
        run: nginx-rs
    spec:
      containers:
      - name: nginx
        image: nginx
```

```bash
kubectl apply -f myreplicaset.yaml
# replicaset.apps/myreplicaset created

kubectl get replicaset  # 축약 시, rs
# NAME            DESIRED   CURRENT   READY   AGE
# myreplicaset    2         2         2       1m
```

```bash
kubectl get pod
# NAME                READY   STATUS      RESTARTS   AGE
# myreplicaset-jc496  1/1     Running     0          6s
# myreplicaset-xr216  1/1     Running     0          6s
```

```bash
# 복제본 개수 확장
kubectl scale rs --replicas <NUMBER> <NAME>
```

```bash
# replica scaling
kubectl scale rs --replicas 4 myreplicaset
# replicaset.apps/rs scaled

kubectl get rs
# NAME            DESIRED   CURRENT   READY   AGE
# myreplicaset    4         4         4       1m

kubectl get pod
# NAME                READY   STATUS      RESTARTS   AGE
# myreplicaset-jc496  1/1     Running     0          2m
# myreplicaset-xr216  1/1     Running     0          2m
# myreplicaset-dc20x  1/1     Running     0          9s
# myreplicaset-3pq2t  1/1     Running     0          9s
```

```bash
kubectl delete pod myreplicaset-jc496
# pod "myreplicaset-jc496" deleted

kubectl get pod
# NAME                READY   STATUS      RESTARTS   AGE
# myreplicaset-xr216  1/1     Running     0          3m
# myreplicaset-dc20x  1/1     Running     0          1m
# myreplicaset-3pq2t  1/1     Running     0          1m
# myreplicaset-0y18b  1/1     Running     0          11s
```

```bash
# ReplicaSet 정리
kubectl delete rs --all
```

## 7.3 Deployment

```yaml
# mydeploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mydeploy
spec:
  replicas: 10
  selector:
    matchLabels:
      run: nginx
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%  
      maxSurge: 25%
  template:
    metadata:
      labels:
        run: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.7.9
```

```bash
kubectl apply --record -f mydeploy.yaml
# deployment.apps/mydeploy created

kubectl get deployment  # 축약 시, deploy
# NAME       READY   UP-TO-DATE   AVAILABLE   AGE
# mydeploy   10/10   10           10          10m

kubectl get rs
# NAME              DESIRED   CURRENT   READY   AGE
# mydeploy-649xxx   10        10        10       1m

kubectl get pod
# NAME                   READY   STATUS       RESTARTS   AGE
# mydeploy-649xxx-bbxx   1/1     Running      0          9s
# mydeploy-649xxx-dtxx   1/1     Running      0          2m9s
# ...
```

```bash
# 이미지 주소 변경
kubectl set image deployment <NAME> <CONTAINER_NAME>=<IMAGE>
```

```bash
# 기존 nginx 버전 1.7.9에서 1.9.1로 업데이트
kubectl set image deployment mydeploy nginx=nginx:1.9.1 --record
# deployment.apps/mydeploy image updated

# 업데이트 진행 상황 확인합니다.
kubectl get pod
# NAME                   READY   STATUS             RESTARTS   AGE
# mydeploy-649xxx-bbxx   1/1     ContainerCreating  0          9s
# mydeploy-649xxx-dtxx   1/1     Running            0          2m9s
# ...

# 배포 상태확인
kubectl rollout status deployment mydeploy
# Waiting for deployment "mydeploy" rollout to finish: 
# 7 out of 10 new replicas have been updated...
# Waiting for deployment "mydeploy" rollout to finish: 
# 7 out of 10 new replicas have been updated...
# Waiting for deployment "mydeploy" rollout to finish: 
# 7 out of 10 new replicas have been updated...
# Waiting for deployment "mydeploy" rollout to finish: 
# 8 out of 10 new replicas have been updated...
# ...
# deployment "mydeploy" successfully rolled out

# 특정 Pod의 이미지 tag 정보를 확인합니다.
kubectl get pod mydeploy-xxx-xxx -o yaml | grep "image: nginx"
#   - image: nginx:1.9.1
```

```bash
# 1.9.1 버전에서 (존재하지 않는) 1.9.21 버전으로 업데이트 (에러 발생)
kubectl set image deployment mydeploy nginx=nginx:1.9.21 --record
# deployment.apps/mydeploy image updated

# Pod의 상태확인
kubectl get pod
# NAME                  READY   STATUS            RESTARTS  AGE
# mydeploy-6498-bbk9v   1/1     Running           0         9m38s
# mydeploy-6498-dt5d7   1/1     Running           0         9m28s
# mydeploy-6498-wrpgt   1/1     Running           0         9m38s
# mydeploy-6498-sbkzz   1/1     Running           0         9m27s
# mydeploy-6498-hclwx   1/1     Running           0         9m26s
# mydeploy-6498-98hd5   1/1     Running           0         9m25s
# mydeploy-6498-5gjrg   1/1     Running           0         9m24s
# mydeploy-6498-4lz4p   1/1     Running           0         9m38s
# mydeploy-6fbf-7kzpf   0/1     ErrImagePull      0         48s
# mydeploy-6fbf-rfgbd   0/1     ErrImagePull      0         48s
# mydeploy-6fbf-v5ms5   0/1     ErrImagePull      0         48s
# mydeploy-6fbf-rccw4   0/1     ErrImagePull      0         48s
# mydeploy-6fbf-ncqd2   0/1     ImagePullBackOff  0         48s
```


```bash
# 지금까지의 배포 히스토리를 확인합니다.
kubectl rollout history deployment mydeploy
# deployment.apps/mydeploy
# REVISION  CHANGE-CAUSE
# 1         kubectl apply --record=true --filename=mydeploy.yaml
# 2         kubectl set image deployment mydeploy nginx=nginx:1.9.1 
#                   --record=true
# 3         kubectl set image deployment mydeploy nginx=nginx:1.9.21 
#                   --record=true

# 잘못 설정된 1.9.21에서 --> 1.9.1로 롤백
kubectl rollout undo deployment mydeploy
# deployment.apps/mydeploy rolled back

kubectl rollout history deployment mydeploy
# deployment.apps/mydeploy
# REVISION  CHANGE-CAUSE
# 1         kubectl apply --record=true --filename=mydeploy.yaml
# 3         kubectl set image deployment mydeploy nginx=nginx:1.9.21 
#                    --record=true
# 4         kubectl set image deployment mydeploy nginx=nginx:1.9.1 
#                    --record=true

kubectl get deployment mydeploy -oyaml | grep image
# image: nginx:1.9.1
```

```bash
# 1.9.1 --> 1.7.9 (revision 1)로 롤백 (처음으로 롤백)
kubectl rollout undo deployment mydeploy --to-revision=1
# deployment.apps/mydeploy rolled back
```

```bash
# 복제본 개수 조절
kubectl scale deployment --replicas <NUMBER> <NAME>
```

```bash
kubectl scale deployment mydeploy --replicas 5
# deployment.apps/mydeploy scaled

# 10개에서 5개로 줄어가는 것을 확인할 수 있습니다.
kubectl get pod
# NAME                  READY   STATUS           RESTARTS  AGE
# mydeploy-6498-bbk9v   1/1     Running          0         9m38s
# mydeploy-6498-dt5d7   1/1     Running          0         9m28s
# mydeploy-6498-wrpgt   1/1     Running          0         9m38s
# mydeploy-6498-sbkzz   1/1     Running          0         9m27s
# mydeploy-6498-98hd5   1/1     Running          0         9m27s
# mydeploy-6498-3srxd   0/1     Terminating      0         9m25s
# mydeploy-6498-5gjrg   0/1     Terminating      0         9m24s
# mydeploy-6498-4lz4p   0/1     Terminating      0         9m38s
# mydeploy-6fbf-7kzpf   0/1     Terminating      0         9m38s
# mydeploy-6fbf-d245c   0/1     Terminating      0         9m38s

# 다시 Pod의 개수를 10개로 되돌립니다.
kubectl scale deployment mydeploy --replicas=10
# deployment.apps/mydeploy scaled

# 5개가 새롭게 추가되어 다시 10개가 됩니다.
kubectl get pod
# NAME                  READY   STATUS              RESTARTS  AGE
# mydeploy-6498-bbk9v   1/1     Running             0         9m38s
# mydeploy-6498-dt5d7   1/1     Running             0         9m28s
# mydeploy-6498-wrpgt   1/1     Running             0         9m38s
# mydeploy-6498-sbkzz   1/1     Running             0         9m27s
# mydeploy-6498-98hd5   1/1     Running             0         9m25s
# mydeploy-6498-30cs2   0/1     ContainerCreating   0         5s
# mydeploy-6fbf-sdjc8   0/1     ContainerCreating   0         5s
# mydeploy-6498-w8fkx   0/1     ContainerCreating   0         5s
# mydeploy-6498-qw89f   0/1     ContainerCreating   0         5s
# mydeploy-6fbf-19glc   0/1     ContainerCreating   0         5s
```

```bash
kubectl edit deploy mydeploy
# apiVersion: apps/v1
# kind: Deployment
# metadata:
# ...
# spec:
#   progressDeadlineSeconds: 600
#   replicas: 10                  # --> 3으로 수정
#   revisionHistoryLimit: 10
#   selector:
#     matchLabels:
#       run: nginx
# 
# <ESC> + :wq
```

```bash
kubectl get pod
# NAME                  READY   STATUS     RESTARTS  AGE
# mydeploy-6498-bbk9v   1/1     Running    0         12m8s
# mydeploy-6498-dt5d7   1/1     Running    0         12m8s
# mydeploy-6498-wrpgt   1/1     Running    0         12m8s
```

```bash
# deployment 쿠버네티스 컨셉](07-02.png)
정리
kubectl delete deploy --all
```
## 7.4 StatefulSet

```yaml
# mysts.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysts
spec:
  serviceName: mysts
  replicas: 3
  selector:
    matchLabels:
      run: nginx
  template:
    metadata:
      labels:
        run: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        volumeMounts:
        - name: vol
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: vol
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
---
apiVersion: v1
kind: Service
metadata:
  name: mysts
spec:
  clusterIP: None
  ports:
  - port: 8080
    protocol: TCP
    targetPort: 80
  selector:
    run: nginx
```

```bash
kubectl apply -f mysts.yaml
# statefulset.apps/mysts created
# service/mysts created

kubectl get statefulset   # 축약 시, sts
# NAME    READY   AGE
# mysts   2/3     20s

kubectl get pod
# NAME      READY   STATUS              RESTARTS   AGE
# mysts-0   1/1     Running             0          29s
# mysts-1   0/1     ContainerCreating   0          20s
# mysts-2   0/1     Pending             0          10s
```

```bash
kubectl exec mysts-0 -- hostname
# mysts-0

kubectl exec mysts-1 -- hostname
# mysts-1
```

```bash
kubectl exec mysts-0 -- sh -c \
  'echo "$(hostname)" > /usr/share/nginx/html/index.html'
kubectl exec mysts-1 -- sh -c \
  'echo "$(hostname)" > /usr/share/nginx/html/index.html'

kubectl exec mysts-0 -- curl -s http://localhost
# mysts-0
kubectl exec mysts-1 -- curl -s http://localhost
# mysts-1
```

```bash
kubectl get persistentvolumeclaim
# NAME          STATUS   VOLUME        CAP  MODE   STORAGECLASS   AGE
# vol-mysts-0   Bound    pvc-09d-xxx   1Gi  RWO    local-path     118s
# vol-mysts-1   Bound    pvc-421-xxx   1Gi  RWO    local-path     109s
# vol-mysts-2   Bound    pvc-x42-xxx   1Gi  RWO    local-path     60s
```

```bash
kubectl scale sts mysts --replicas=0
# statefulset.apps/mysts scaled

kubectl get pod
# NAME      READY   STATUS       RESTARTS   AGE
# mysts-0   1/1     Running      0          29s
# mysts-1   0/1     Terminating  0          20s
```

### StatefulSet 예제

`StatefulSet` 리소스의 좋은 사용 예시로 MySQL DB 클러스터를 구축하는 예제가 쿠버네티스 공식 사이트에 존재하지만 내용이 비교적 장황하여 본래 리소스의 특징을 파악하기 어려워 간단한 NGINX 예제로 대체하였습니다. 다음 페이지에서 직접 MySQL 클러스터 구축 예제를 확인해 보시기 바랍니다.

[https://kubernetes.io/docs/tasks/run-application/run-replicated-stateful-application](https://kubernetes.io/docs/tasks/run-application/run-replicated-stateful-application)


```bash
kubectl delete sts mysts
kubectl delete svc mysts
kubectl delete pvc --all
```

## 7.5 DaemonSet

```yaml
# fluentd.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      containers:
      - name: fluentd
        image: quay.io/fluentd_elasticsearch/fluentd:v2.5.2
        volumeMounts:
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

```bash
kubectl apply -f fluentd.yaml
# daemonset.apps/fluentd created

kubectl get daemonset   # 축약 시, ds
# NAME      DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE ..
# fluentd   2         2         2       2            2                ..

kubectl get pod -owide
# NAME           READY  STATUS    RESTARTS  AGE   IP          NODE    ..
# fluentd-q9vcc  1/1    Running   0         92s   10.42.0.8   master  ..
# fluentd-f3gt3  1/1    Running   0         92s   10.42.0.10  worker  ..

kubectl logs fluentd-q9vcc
# 2020-07-05 04:12:05 +0000 [info]: parsing config file is succeeded ..
# 2020-07-05 04:12:05 +0000 [info]: using configuration file: <ROOT>
#   <match fluent.**>
#     @type null
#   </match>
# </ROOT>
# 2020-07-05 04:12:05 +0000 [info]: starting fluentd-1.4.2 pid=1 ..
# 2020-07-05 04:12:05 +0000 [info]: spawn command to main: cmdline=..
# ...
```

```bash
kubectl delete ds --all
```

## 7.6 Job & CronJob

### 7.6.1 Job

```python
# train.py
import os, sys, json
import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import RMSprop

#####################
# parameters
#####################
epochs = int(sys.argv[1])
activate = sys.argv[2]
dropout = float(sys.argv[3])
print(sys.argv)
#####################

batch_size, num_classes, hidden = (128, 10, 512)
loss_func = "categorical_crossentropy"
opt = RMSprop()

# preprocess
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.reshape(60000, 784)
x_test = x_test.reshape(10000, 784)
x_train = x_train.astype('float32') / 255
x_test = x_test.astype('float32') / 255

# convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

# build model
model = Sequential()
model.add(Dense(hidden, activation='relu', input_shape=(784,)))
model.add(Dropout(dropout))
model.add(Dense(num_classes, activation=activate))
model.summary()

model.compile(loss=loss_func, optimizer=opt, metrics=['accuracy'])

# train
history = model.fit(x_train, y_train, batch_size=batch_size, 
        epochs=epochs, validation_data=(x_test, y_test))

score = model.evaluate(x_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
```

```Dockerfile
# Dockerfile
FROM python:3.6.8-stretch

RUN pip install tensorflow==1.5 keras==2.0.8 h5py==2.7.1

COPY train.py .

ENTRYPOINT ["python", "train.py"]
```

```bash
# 도커 이미지 빌드
docker build . -t $USERNAME/train
# Sending build context to Docker daemon  3.249MB
# Step 1/4 : FROM python:3.6.8-stretch
# 3.6.8-stretch: Pulling from library/python
# 6f2f362378c5: Pull complete
# ...

# 도커 이미지 업로드를 위해 도커허브에 로그인합니다.
docker login
# Login with your Docker ID to push and pull images from Docker Hub. ..
# Username: $USERNAME
# Password:
# WARNING! Your password will be stored unencrypted in /home/..
# Configure a credential helper to remove this warning. See
# https://docs.docker.com/engine/reference/commandline/..
# 
# Login Succeeded

# 도커 이미지 업로드
docker push $USERNAME/train
# The push refers to repository [docker.io/$USERNAME/train]
```

```yaml
# job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: myjob
spec:
  template:
    spec:
      containers:
      - name: ml
        image: $USERNAME/train
        args: ['3', 'softmax', '0.5']
      restartPolicy: Never
  backoffLimit: 2
```

```bash
# Job 생성
kubectl apply -f job.yaml
# job.batch/myjob created

# Job 리소스 확인
kubectl get job
# NAME    COMPLETIONS   DURATION   AGE
# myjob   0/1           9s         9s

# Pod 리소스 확인
kubectl get pod
# NAME          READY   STATUS      RESTARTS   AGE
# myjob-l5thh   1/1     Running     0          9s

# 로그 확인
kubectl logs -f myjob-l5thh 
# ...
# Layer (type)                 Output Shape              Param #
# =================================================================
# dense_1 (Dense)              (None, 512)               401920
# ...

# Pod 완료 확인
kubectl get pod
# NAME          READY   STATUS      RESTARTS   AGE
# myjob-l5thh   0/1     Completed   0          3m27s

# Job 완료 확인
kubectl get job
# NAME    COMPLETIONS   DURATION   AGE
# myjob   1/1           51s         4m
```

```yaml
# job-bug.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: myjob-bug
spec:
  template:
    spec:
      containers:
      - name: ml
        image: $USERNAME/train
        # int 타입이 아닌 string 타입 전달
        args: ['bug-string', 'softmax', '0.5']
      restartPolicy: Never
  backoffLimit: 2
```

```bash
kubectl apply -f job-bug.yaml

# 2번 재시도 후(총 3번 실행) failed
kubectl get pod
# NAME               READY   STATUS              RESTARTS   AGE
# myjob-bug-8f867      0/1     Error               0          6s
# myjob-bug-s23xs      0/1     Error               0          4s
# myjob-bug-jz2ss      0/1     ContainerCreating   0          1s

kubectl get job myjob-bug -oyaml | grep type
# type: Failed

# 에러 원인 확인
kubectl logs -f myjob-bug-jz2ss
# /usr/local/lib/python3.6/site-packages/tensorflow/python/framework/
#   dtypes.py:502: FutureWarning: Passing (type, 1) or '1type' 
#   as a synonym of type is deprecated; in a future version of numpy, 
#   it will be understood as (type, (1,)) / '(1,)type'.
#   np_resource = np.dtype([("resource", np.ubyte, 1)])
# Traceback (most recent call last):
#   File "train.py", line 11, in <module>
#    epochs = int(sys.argv[1])
# ValueError: invalid literal for int() with base 10: 'bug-string'
```

```bash
kubectl delete job --all
```

### 7.6.2 CronJob

```yaml
# cronjob.yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: hello
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox
            args:
            - /bin/sh
            - -c
            - date; echo Hello from the Kubernetes cluster
          restartPolicy: OnFailure
```

```bash
kubectl apply -f cronjob.yaml
# cronjob.batch/hello created

kubectl get cronjob
# NAME    SCHEDULE      SUSPEND   ACTIVE   LAST SCHEDULE   AGE
# hello   */1 * * * *   False     0        <none>          4s

kubectl get job
# NAME               COMPLETIONS   DURATION   AGE
# hello-1584873060   0/1           3s         3s
# hello-1584873060   0/1           3s         62s
```

```bash
kubectl delete cronjob --all
```
