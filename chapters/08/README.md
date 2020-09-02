# 8. helm 패키지 매니저

## 8.1 `helm`이란

### 8.1.1 `helm` 설치

```bash
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash -s -- --version v3.2.2
```

### 8.1.2 `chart` 생성

```bash
helm create mychart
# Creating mychart

ls mychart
# Chart.yaml  charts  templates  values.yaml
```

```bash
ls mychart/templates
# NOTES.txt
# _helpers.tpl
# deployment.yaml
# ingress.yaml
# service.yaml
# serviceaccount.yaml
# tests/
```

```yaml
# mychart/templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}         # 서비스 타입 지정
  ports:
    - port: {{ .Values.service.port }}     # 서비스 포트 지정
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "mychart.selectorLabels" . | nindent 4 }}
```

```yaml
# values.yaml
replicaCount: 1

image:
  repository: nginx
  pullPolicy: IfNotPresent

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

...
# 약 40줄
service:
  type: LoadBalancer  # 기존 ClusterIP
  port: 8888          # 기존 80

...
```

### 8.1.3 chart 설치

```bash
helm install foo ./mychart
# NAME: foo
# LAST DEPLOYED: Tue Mar 10 14:26:02 2020
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# NOTES:
#    ....
```

```bash
# service 리소스를 조회합니다.
kubectl get svc
# NAME         TYPE          CLUSTER-IP      EXTERNAL-IP    PORT(S)   
# kubernetes   ClusterIP     10.43.0.1       <none>         443/TCP   
# foo-mychart  LoadBalancer  10.43.142.107   10.0.1.1       8888:32597/TCP 
```

### 8.1.4 `chart` 리스트 조회

```bash
# 설치된 chart 리스트 확인하기
helm list
# NAME    NAMESPACE  REVISION  UPDATED   STATUS    CHART          APP VER
# foo     default    1         2020-3-1  deployed  mychart-0.1.0  1.16.0

# 다른 네임스페이스에는 설치된 chart가 없습니다.
helm list -n kube-system
# NAME   NAMESPACE   REVISION    UPDATED STATUS  CHART   APP   VERSION
```

### 8.1.5 chart 랜더링

```bash
helm template foo ./mychart > foo-output.yaml

cat foo-output.yaml
# 전체 YAML 정의서 출력
```

### 8.1.6 chart 업그레이드

```yaml
# values.yaml
...

service:
  type: NodePort    # 기존 LoadBalancer
  port: 8888        
...
```

```bash
helm upgrade foo ./mychart
# Release "foo" has been upgraded. Happy Helming!
# NAME: foo
# LAST DEPLOYED: Mon Jul  6 19:26:35 2020
# NAMESPACE: default
# STATUS: deployed
# REVISION: 2
# ...

kubectl get svc
# NAME        TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)          
# kubernetes  ClusterIP   10.43.0.1      <none>        443/TCP   
# foo         NodePort    10.43.155.85   <none>        8888:32160/TCP 

helm list
# NAME     NAMESPACE  REVISION   UPDATED    STATUS      CHART      
# foo      default    2          2020-3-2   deployed    mychart-0.1.0 
```

### 8.1.7 chart 배포상태 확인

```bash
helm status foo
# Release "foo" has been upgraded. Happy Helming!
# NAME: foo
# LAST DEPLOYED: Mon Jul  6 19:26:35 2020
# NAMESPACE: default
# STATUS: deployed
# REVISION: 2
# ...
```

### 8.1.8 `chart` 삭제

```bash
helm delete foo
# release "foo" uninstalled

helm list
# NAME   NAMESPACE   REVISION    UPDATED STATUS  CHART   APP   VERSION
```

## 8.2 원격 레포지토리

### 8.2.1 레포지토리 추가

```bash
# stable repo 추가
helm repo add stable https://kubernetes-charts.storage.googleapis.com
```

### 8.2.2 레포지토리 업데이트

```bash
# repo update
helm repo update
# ...Successfully got an update from the "stable" chart repository
# Update Complete. ⎈ Happy Helming!⎈
```

### 8.2.3 레포지토리 조회

```bash
# 현재 등록된 repo 리스트
helm repo list
# NAME    URL
# stable  https://kubernetes-charts.storage.googleapis.com
```

### 8.2.4 레포지토리내 chart 조회

```bash
# stable 레포 안의 chart 리스트
helm search repo stable
# NAME                    CHART VERSION  APP VERSION    DESCRIPTION
# stable/aerospike        0.3.2          v4.5.0.5       A Helm chart ..
# stable/airflow          7.1.4          1.10.10        Airflow is a ..
# stable/ambassador       5.3.2          0.86.1         DEPRECATED ...
# stable/anchore-engine   1.6.8          0.7.2          Anchore container
# stable/apm-server       2.1.5          7.0.0          The server ...
# ...

helm search repo stable/airflow
# NAME            CHART VERSION   APP VERSION     DESCRIPTION
# stable/airflow  7.2.0           1.10.10         Airflow is a plat...
```

다음 주소에서 `stable` 레포지토리 외에 다양한 원격 저장소를 조회해 볼 수 있습니다. 

helm 허브: [https://hub.helm.sh/charts](https://hub.helm.sh/charts)

## 8.3 외부 chart 설치 (WordPress)

### 8.3.1 `chart install`

```bash
helm install wp stable/wordpress \
    --version 9.0.3 \
    --set service.port=8080 \
    --namespace default
# WARNING: This chart is deprecated
# NAME: wp
# LAST DEPLOYED: Mon Jul  6 20:44:55 2020
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# NOTES:
# ...

kubectl get pod
# NAME             READY   STATUS              RESTARTS   AGE
# svclb-wp-xv6b6   2/2     Running             0          6s
# wp-mariadb-0     0/1     ContainerCreating   0          6s
# wp-6d78b5c456    0/1     Running             0          6s

kubectl get svc
# NAME         TYPE          CLUSTER-IP     EXTERNAL-IP   PORT(S)     
# kubernetes   ClusterIP     10.43.0.1      <none>        443/TCP
# wp-mariadb   ClusterIP     10.43.90.229   <none>        3306/TCP
# wp           LoadBalancer  10.43.167.4    10.0.1.1      8080:30887/TCP,...
```

```yaml
# values.yaml
...
service:
  port: 80  -->  8080
...
```

```bash
# curl로 접근해 봅니다.
curl localhost:8080
```

### 8.3.2 `chart fetch`

```bash
helm fetch --untar stable/wordpress --version 9.0.3

ls wordpress/
# Chart.yaml  README.md  charts  requirements.lock  
# requirements.yaml  templates  values.schema.json  values.yaml

# 사용자 입맛에 따라 세부 설정값 변경
vim wordpress/values.yaml
# ...

helm install wp-fetch ./wordpress
# WARNING: This chart is deprecated
# NAME: wp-fetch
# LAST DEPLOYED: Mon Jul  6 20:44:55 2020
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# NOTES:
# ...
```

### Clean up

```bash
helm delete wp
helm delete wp-fetch
kubectl delete pvc data-wp-mariadb-0 data-wp-fetch-mariadb-0
```
