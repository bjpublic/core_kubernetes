# 16. 사용자 정의 리소스

## 16.1 사용자 정의 리소스란

### 16.1.1 Custom Resource

```yaml
# mypod-crd.yaml
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: mypods.crd.example.com
spec:
  group: crd.example.com
  version: v1
  scope: Namespaced
  names:
    plural: mypods   # 복수 이름
    singular: mypod  # 단수 이름
    kind: MyPod      # Kind 이름
    shortNames:      # 축약 이름
    - mp
```

```bash
# crd 생성
kubectl apply -f mypod-crd.yaml
# customresourcedefinition.apiextensions.k8s.io/mypods.crd.example.com created

# crd 리소스 확인
kubectl get crd | grep mypods
# NAME                     CREATED AT          
# mypods.crd.example.com   2020-06-14T09:33:32Z          
```

```bash
# MyPod 리소스 생성
cat << EOF | kubectl apply -f -
apiVersion: "crd.example.com/v1"
kind: MyPod
metadata:
  name: mypod-test
spec:
  uri: "any uri"
  customCommand: "custom command"
  image: nginx
EOF
# mypod.crd.example.com/mypod-test created

kubectl get mypod
# NAME         AGE
# mypod-test   3s

# 축약형인, mp로도 조회가 가능합니다.
kubectl get mp
# NAME         AGE
# mypod-test   3s

# MyPod의 상세 정보를 조회합니다.
kubectl get mypod mypod-test -oyaml
# apiVersion: crd.example.com/v1
# kind: MyPod
# metadata:
#   ...
#   name: mypod-test
#   namespace: default
#   resourceVersion: "723476"
#   selfLink: /apis/crd.example.com/v1/namespaces/default/mypods/mypod-test
#   uid: 50dd0cc8-0c1a-4f43-854b-a9c212e2046d
# spec:
#   customCommand: custom command
#   image: nginx
#   uri: any uri

# MyPod를 삭제합니다.
kubectl delete mp mypod-test
# mypod.crd.example.com "mypod-test" deleted
```

### 16.1.2 Custom Controller

```bash
# MyPod 정의
struct MyPod {
  Uri string
  CustomCommand string
	...
}


def main {
	# 무한루프
    for {
    	# 신규 이벤트
        desired := apiServer.getDesiredState(MyPod)
        # 기존 이벤트
        current := apiServer.getCurrentState(MyPod)
        
        # 변경점 발생시(수정,생성,삭제), 특정 동작 수행
        if desired != current {
            makeChanges(desired, current)	
        }
    }
}
```

## 16.2 Operator 패턴

### 16.2.1 Operator tools

Operator를 쿠버네티스 API를 이용하여 처음부터 개발하는 것도 가능하지만 Operator를 편리하게 만들 수 있게 제공하는 툴들이 이미 존재합니다.

- `kubebuilder`: [https://book.kubebuilder.io](https://book.kubebuilder.io)
- `Operator Framework`: 
- `Metacontroller`: 
- `KUDO`: 

## 16.3 유용한 Operators

### 16.3.1 MinIO Operator

#### MinIO CRD 및 Controller 설치

```bash
# crd 및 custom controller 생성
kubectl apply -f https://raw.githubusercontent.com/minio/operator/2.0.9/minio-operator.yaml
# customresourcedefinition.apiextensions.k8s.io/minioinstances.operator.min.io created
# clusterrole.rbac.authorization.k8s.io/minio-operator-role created
# serviceaccount/minio-operator created
# clusterrolebinding.rbac.authorization.k8s.io/minio-operator-binding created
# deployment.apps/minio-operator created

# minio operator 실행 확인
kubectl get pod
# NAME                     READY   STATUS    RESTARTS  AGE
# minio-operator-84b88xx   1/1     Running   0         3m59s
```

#### MinIO CRD instance 생성

```yaml
# minio-instance.yaml

# minio에서 사용할 access 정보
apiVersion: v1
kind: Secret
metadata:
  name: minio-creds-secret
type: Opaque
data:
  accesskey: bWluaW8=      # minio
  secretkey: bWluaW8xMjM=  # minio123
---
# MinIO Service 리소스
apiVersion: v1
kind: Service
metadata:
  name: minio-service
spec:
  type: ClusterIP
  ports:
    - port: 9000
      targetPort: 9000
      protocol: TCP
  selector:
    app: minio-dev
---
# MinIO 사용자 정의 리소스
apiVersion: operator.min.io/v1
kind: MinIOInstance
metadata:
  name: minio-dev
spec:
  metadata:
    labels:
      app: minio-dev
    annotations:
      prometheus.io/path: /minio/prometheus/metrics
      prometheus.io/port: "9000"
      prometheus.io/scrape: "true"
  image: minio/minio:RELEASE.2020-06-03T22-13-49Z
  serviceName: minio-internal-service
  zones:
    - name: "zone-0"
      servers: 1
  volumesPerServer: 1
  mountPath: /export
  volumeClaimTemplate:
    metadata:
      name: data
    spec:
      accessModes:
        - ReadWriteOnce
      resources:
        requests:
          storage: 1Gi
  credsSecret:
    name: minio-creds-secret
  podManagementPolicy: Parallel
  requestAutoCert: false
  certConfig:
    commonName: ""
    organizationName: []
    dnsNames: []
  liveness:
    initialDelaySeconds: 120
    periodSeconds: 60
  readiness:
    initialDelaySeconds: 120
    periodSeconds: 60
```

```bash
kubectl apply -f minio-instance.yaml
# secret/minio-creds-secret created
# service/minio-service created
# minioinstance.operator.min.io/minio-dev created

# MinIOInstance 리소스를 조회합니다.
kubectl get MinIOInstance
# NAME        CURRENT STATE
# minio-dev   Ready

# Pod가 ready 될 때까지 시간이 조금 걸립니다.
kubectl get pod
# NAME                    READY   STATUS    RESTARTS   AGE
# minio-operator-848xxx   1/1     Running   0          30s
# minio-dev-0             1/1     Running   0          12s

kubectl get svc
# NAME                    TYPE        CLUSTER-IP      ...   PORT(S)    AGE
# kubernetes              ClusterIP   10.43.0.1       ...   443/TCP    10h
# minio-service           ClusterIP   10.43.146.111   ...   9000/TCP   23s
# minio-internal-service  ClusterIP   10.43.112.37    ...   9000/TCP   21s
# minio-dev-hl-svc        ClusterIP   None            ...   9000/TCP   19s
```

```bash
# minio instance 삭제
kubectl delete -f minio-instance.yaml
# minio operator 삭제
kubectl delete -f https://raw.githubusercontent.com/minio/operator/2.0.9/minio-operator.yaml
```

### 16.3.2 Prometheus-Operator

```bash
helm install mon stable/prometheus-operator --version 8.16.1

# prometheus라는 사용자 정의 리소스 확인
kubectl get prometheuses
# NAME                                VERSION   REPLICAS   AGE
# mon-prometheus-operator-prometheus  v2.18.1   1          17s

# Prometheus 사용자 정의 리소스
kubectl get prometheuses mon-prometheus-operator-prometheus -oyaml
# apiVersion: monitoring.coreos.com/v1
# kind: Prometheus
# metadata:
#   annotations:
#     meta.helm.sh/release-name: mon
#     meta.helm.sh/release-namespace: default
#   generation: 1
#   labels:
#     app: prometheus-operator-prometheus
#     app.kubernetes.io/managed-by: Helm
#     chart: prometheus-operator-8.14.0
#     heritage: Helm
#   ....

helm delete mon
```

### 16.3.3 Helm Operator

```yaml
# myHelmRelease.yaml
apiVersion: helm.fluxcd.io/v1
kind: HelmRelease
metadata:
  name: rabbit
  namespace: default
spec:
  releaseName: rabbitmq
  chart:
    repository: https://kubernetes-charts.storage.googleapis.com/
    name: rabbitmq
    version: 3.3.6
  values:
    replicas: 1
```

#### Helm Operator 설치

```bash
# CustomResourceDefinition 설정
kubectl apply -f https://raw.githubusercontent.com/fluxcd/helm-operator/1.0.1/deploy/crds.yaml
# customresourcedefinition.apiextensions.k8s.io/helmreleases.helm.fluxcd.io created  

# helm repo 등록
helm repo add fluxcd https://charts.fluxcd.io
# "fluxcd" has been added to your repositories  

# helm-operator 설치
helm install helm-operator fluxcd/helm-operator \
    --namespace flux \
    --version 1.1.0 \
    --set helm.versions=v3
# Release "helm-operator" does not exist. Installing it now.
# NAME: helm-operator
# LAST DEPLOYED: Sun Jul 12 05:43:14 2020
# NAMESPACE: flux
# STATUS: deployed
# REVISION: 1
# TEST SUITE: None
# NOTES:
# ...

# 설치 확인
kubectl get pod -nflux
# NAME               READY   STATUS    RESTARTS
# helm-operator-xxx  1/1     Running   0     
```

#### HelmRelease를 이용한 chart 설치

```yaml
# jenkins.yaml
apiVersion: helm.fluxcd.io/v1
kind: HelmRelease
metadata:
  name: jenkins
  namespace: default
spec:
  releaseName: jenkins
  chart:
    repository: https://kubernetes-charts.storage.googleapis.com
    name: jenkins
    version: 2.3.0
  values:
    master:
      adminUser: "jenkins"
      resources:
        limits:
          cpu: "500m"
          memory: "512Mi"
      serviceType: LoadBalancer
      servicePort: 8080
```

```bash
helm fetch --untar stable/jenkins --version 2.3.0

# jenkins chart의 values.yaml과 비교해 보시기 바랍니다.
vim jenkins/values.yaml
```

```bash
# helm install jenkins stable/jenkins
kubectl apply -f jenkins.yaml
# helmrelease.helm.fluxcd.io/jenkins created 

# helm list
kubectl get helmrelease  # 축약이름 hr
# NAME      RELEASE   PHASE       STATUS   MESSAGE           AGE
# jenkins             Succeeded            Release was ...   15s

# 상세 리소스 조회
kubectl get hr jenkins -oyaml

# Describe resource
kubectl describe hr jenkins
```

```bash
helm list
# NAME     NAMESPACE   REVISION   STATUS     CHART           APP VERSION
# jenkins  default     1          deployed   jenkins-1.15.0  lts

helm status jenkins
# NAME: jenkins
# ...
# REVISION: 1
# NOTES:
# 1. Get your 'admin' user password by running:
#   printf $(kubectl get secret --namespace default jenkins -o 
#    jsonpath="{.data.jenkins-admin-password}" | base64 --decode);echo
# 2. Get the Jenkins URL to visit by running these commands in the same
# ...
```

```bash
kubectl get pod
# NAME                      READY   STATUS    RESTARTS   AGE
# svclb-jenkins-jb5j9       1/1     Running   0          4m37s
# svclb-jenkins-qbvrm       1/1     Running   0          4m37s
# jenkins-7c55757f9c-758lv  2/2     Running   0          5m9s

kubectl get svc
# NAME           TYPE          CLUSTER-IP    EXTERNAL-IP    PORT(S)         
# kubernetes     ClusterIP     10.43.0.1     <none>         443/TCP         
# jenkins-agent  ClusterIP     10.43.51.30   <none>         50000/TCP       
# jenkins        LoadBalancer  10.43.94.188  172.31.17.208  8080:32487/TCP  
```

### Clean up

```bash
# helm instance 삭제
kubectl delete -f jenkins.yaml

# helm operator 삭제
helm delete helm-operator -n flux
```
