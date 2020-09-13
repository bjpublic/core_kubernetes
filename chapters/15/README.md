# 15. CI/CD

## 15.2 CI 파이프라인

### 15.2.1 Jenkins

```bash
# 먼저 jenkins chart를 다운 받습니다.
helm fetch --untar stable/jenkins --version 2.3.0

vim jenkins/values.yaml
```

```yaml
# jenkins/values.yaml 수정
# 약 375번째 line, ingress 설정
  ingress:
    enable: true   # 기존 false
    ...
    annotations:
      kubernetes.io/ingress.class: nginx   # 추가
        
    hostName: jenkins.10.0.1.1.sslip.io    # 공인IP 입력
```

```bash
# jenkins 설치
helm install jenkins ./jenkins

# NAME: jenkins
# LAST DEPLOYED: Sat Mar 14 00:16:01 2020
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# NOTES:
# 1. Get your 'admin' user password by running:
#   printf $(kubectl get secret --namespace default jenkins -o 
# jsonpath="{.data.jenkins-admin-password}" | base64 --decode);echo
# 
# 2. Visit http://jenkins.10.0.0.1.sslip.io
# 
# 3. Login with the password from step 1 and the username: admin
```

```bash
watch kubectl get pod
# NAME                        READY   STATUS      RESTARTS   AGE
# jenkins-68d5bcc94b-r99kz    0/1     Init:0/1    0          13s

kubectl wait --for condition=Ready pod jenkins-68d5bcc94b-r99kz
# pod/jenkins-68d5bcc94b-r99kz condition met
```

- 아이디: `admin`
- 비밀번호: 아래 명령을 통해 확인

```bash
printf $(kubectl get secret --namespace default jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode);echo
# 1Ctidon3hh
```

1. `New item` > `Free style project` > `Enter an item name`: `myfirstjob` > OK
2. `Build` > `Add build step` > `Execute shell`
3. `Command` > `echo "hello world!"` 입력 > `Save`
4. `Build Now` > `#1` > `Console Output`

```bash
watch kubectl get pod
# NAME                       READY   STATUS              RESTARTS   AGE
# jenkins-68d5bcc94b-r99kz   1/1     Running             0          49m
# default-rrl40              0/1     ContainerCreating   0          15s
```

### 15.2.2 CI 파이프라인

```bash
# checkout
git clone $PROJECT
git checkout $BRANCH

# build
docker build . -t $USERNAME/$PROJECT

# test
docker run --entrypoint /test $USERNAME/$PROJECT

# push
docker login --username $USERNAME --password $PASSWORD
docker push $USERNAME/$PROJECT
```

### 15.2.3 도커 안에 도커

도커 in 도커에 대한 더 자세한 내용은 다음 글을 참고해 보시기 바랍니다.

[https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci](https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci)

```bash
# docker 라는 이미지를 실행하면서 도커 소켓을 볼륨으로 연결해 줍니다.
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock docker
# Unable to find image 'docker:latest' locally 
# ...

# 컨테이너 내부에서 host 도커의 프로세스를 확인할 수 있습니다.
$root@43bf40690fa9:/# docker ps
# CONTAINER ID   IMAGE               COMMAND         CREATED         ... 
# 43bf40690fa9   docker              "docker-en..."  13 seconds ago  ... 
# e773f2075df4   rancher/pause:3.1   "/pause"        5 hours ago     ...
# ...

$root@43bf40690fa9:/# exit
```

### 15.2.4 Jenkins Pipeline

다음과 같이 진행합니다.

1. `Jenkins` > `Manage Jenkins` > `Manage Credentials` > `Jenkins` > `Global credentials` > `Add Credentials`
    - `Scope`: Global
    - `Kind`: Username with password
    - `ID`: dockerhub
    - `Username`: 도커허브 아이디
    - `Password`: 도커허브 비밀번호
2. `Jenkins` > `New Item` > `Pipeline` > `Enter Name`: `myfirstpipeline` > `Pipeline` > `OK`
3. `Pipeline Definition: Pipeline script` > 다음 `Jenkinsfile` 스크립트 삽입
4. `Jenkins` > `myfirstpipeline` > `Build Now`

```groovy
# Jenkinsfile
pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: git
    image: alpine/git
    tty: true 
    command: ["cat"]
    env:
    - name: PROJECT_URL
      value: https://github.com/bjpublic/core_kubernetes.git 
  - name: docker
    image: docker
    tty: true 
    command: ["cat"]
    env:
    - name: PROJECT_NAME
      value: core_kubernetes
    volumeMounts:
    - mountPath: /var/run/docker.sock
      name: docker-socket
  volumes:
  - name: docker-socket
    hostPath:
      path: /var/run/docker.sock
'''
        }
    }
    stages {
      stage('Checkout') {
        steps {
          container('git') {
            // 소스코드 checkout  
            sh "git clone \$PROJECT_URL"
          }
        }
      } 
      stage('Build') {
        steps {
          container('docker') {
            // 도커 빌드
            sh """
            cd \$PROJECT_NAME/pipeline-sample
            docker build -t \$PROJECT_NAME .
            """
          }
        }
      }
      stage('Test') {
        steps {
          container('docker') {
            // 이미지 테스트
            sh "docker run --entrypoint /test \$PROJECT_NAME"
          }
        }
      }
      stage('Push') {
        steps {
          container('docker') {
            // 도커헙 계정 정보 가져오기 
            withCredentials([[$class: 'UsernamePasswordMultiBinding',
              credentialsId: 'dockerhub',
              usernameVariable: 'DOCKERHUB_USER',
              passwordVariable: 'DOCKERHUB_PASSWORD']]) {
              // 이미지 패키징 & 업로드
              sh """
                docker login -u ${DOCKERHUB_USER} -p ${DOCKERHUB_PASSWORD}
                docker tag \$PROJECT_NAME ${DOCKERHUB_USER}/\$PROJECT_NAME
                docker push ${DOCKERHUB_USER}/\$PROJECT_NAME
              """
            }
          }
        }
      }
    }
}
```

### Clean up

```bash
helm delete jenkins
```

## 15.3 GitOps를 이용한 CD

### 15.3.4 FluxCD

FluxCD 홈페이지: [https://fluxcd.io](https://fluxcd.io/)

```bash
# fluxcd repo 추가
helm repo add fluxcd https://charts.fluxcd.io
# "fluxcd" has been added to your repositories

helm repo update
# ...Successfully got an update from the "fluxcd" chart repository 

# crd 생성
kubectl apply -f https://raw.githubusercontent.com/fluxcd/helm-operator/master/deploy/crds.yaml
# customresourcedefinition.apiextensions.k8s.io/helmreleases.helm.fluxcd.io created

# 네임스페이스 생성
kubectl create ns flux
# namespace/flux created
```


- deployment.yaml
- service.yaml

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mynginx
spec:
  replicas: 1
  selector:
    matchLabels:
      run: mynginx
  template:
    metadata:
      labels:
        run: mynginx
    spec:
      containers:
      - image: nginx
        name: mynginx
        ports:
        - containerPort: 80
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mynginx
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    run: mynginx
```

```bash
helm install get-started fluxcd/flux \
   --version 1.4.0 \
   --set git.url=https://github.com/hongkunyoo/gitops-get-started.git \
   --set git.readonly=true \
   --set git.path=gitops \
   --namespace flux
# Release "get-started" has been upgraded. Happy Helming!
# NAME: get-started
# LAST DEPLOYED: Thu Jun 11 15:26:37 2020
# NAMESPACE: flux
# STATUS: deployed
# ...
```

```bash
# pod 생성 확인
kubectl get pod
# NAME                     READY   STATUS    RESTARTS   AGE
# mynginx-d5d4f5fbd-hrffl  1/1     Running   0          20s

# service 생성 확인
kubectl get svc
# NAME     TYPE       CLUSTER-IP      EXTERNAL-IP    PORT(S)     AGE
# mynginx  ClusterIP  10.43.207.142   <none>         80/TCP      20s
```

```bash
helm delete get-started -nflux
kubectl delete deploy mynginx
kubectl delete svc mynginx
```

### 15.3.5 ArgoCD

#### ArgoCD 설치

```bash
kubectl create namespace argocd
# namespace/argocd created

kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
# customresourcedefinition.apiextensions.k8s.io/applications.argoproj.io created
# customresourcedefinition.apiextensions.k8s.io/appprojects.argoproj.io created
# serviceaccount/argocd-application-controller created
# serviceaccount/argocd-dex-server created
# ...
```

```yaml
# argocd-ingress.yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: argocd
  namespace: argocd
  annotations:
    cert-manager.io/cluster-issuer: http-issuer
    kubernetes.io/ingress.class: nginx
    kubernetes.io/tls-acme: "true"
    nginx.ingress.kubernetes.io/backend-protocol: HTTPS
    nginx.ingress.kubernetes.io/ssl-passthrough: "true"
spec:
  rules:
  - host: argocd.10.0.1.1.sslip.io
    http:
      paths:
      - path: /
        backend:
          serviceName: argocd-server
          servicePort: https
  tls:
  - hosts:
    - argocd.10.0.1.1.sslip.io
    secretName: argocd-tls
```

```bash
kubectl apply -f argocd-ingress.yaml
# ingress.networking.k8s.io/argocd created
```

- 아이디: admin
- 비밀번호: 다음 명령를 이용하여 비밀번호를 확인합니다.

```bash
kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-server \
    -o name | cut -d'/' -f 2
# argocd-server-6766455855-pzdrv    --> 비밀번호
```

#### ArgoCD 배포

- `Application Name`: gitops-get-started
- `Project`: default
- `Sync Policy`: Manual
- `Repository URL`: `https://github.com/bjpublic/core_kubernetes.git`
- `Revision`: HEAD
- `Path`: gitops
- `Cluster`: in-cluster
- `Namespace`: default
- `Directory Recurse`: Unchecked

### Clean up

```bash
kubectl delete -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl delete ingress argocd -n argocd
kubectl delete deploy mynginx
kubectl delete svc mynginx
```

## 15.4 로컬 쿠버네티스 개발

#### skaffold 설치

```bash
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
sudo install skaffold /usr/local/bin/
```

### 15.4.2 skaffold 세팅

```python
# app.py
from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run()
```

```Dockerfile
# Dockerfile
FROM python:3.7

RUN pip install flask
ADD app.py .

ENTRYPOINT ["python", "app.py"]
```

```yaml
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: skaffold-flask
spec:
  containers:
  - image: <USERNAME>/flask   # 각 사용자 docker hub 계정을 입력합니다.
    name: flask
```

```bash
ls
# app.py    Dockerfile    pod.yaml
```

```bash
skaffold init
# apiVersion: skaffold/v2beta5
# kind: Config
# metadata:
#   name: some-directory
# build:
#   artifacts:
#   - image: <USERNAME>/flask
# deploy:
#   kubectl:
#     manifests:
#     - pod.yaml
# 
# Do you want to write this configuration to skaffold.yaml? [y/n]: y
# Configuration skaffold.yaml was written

ls 
# app.py    Dockerfile    pod.yaml    skaffold.yaml
```

```bash
docker login
# Login with your Docker ID to push and pull images from Docker Hub. ..
# Username: <USERNAME>
# Password:
# WARNING! Your password will be stored unencrypted in ...
# Configure a credential helper to remove this warning. See
# https://docs.docker.com/engine/reference/commandline/...
# 
# Login Succeeded
```

### 15.4.3 skaffold를 이용한 배포

```bash
skaffold run
# Generating tags...
#  - <USERNAME>/flask -> <USERNAME>/flask:latest
# Some taggers failed. Rerun with -vdebug for errors.
# ...
```

```bash
kubectl get pod
# NAME             READY   STATUS              RESTARTS   AGE
# skaffold-flask   0/1     ContainerCreating   0          2m21s
```

```bash
# 기존 pod 삭제
kubectl delete pod skaffold-flask
# pod "skaffold-flask" deleted

skaffold run --tail
# ...
# Press Ctrl+C to exit
# [skaffold-flask flask] starting app
# [skaffold-flask flask]  * Serving Flask app "app" (lazy loading)
# [skaffold-flask flask]  * Environment: production
# [skaffold-flask flask]    WARNING: This is a development server. Do not 
#                                  use it in a production deployment.
# [skaffold-flask flask]    Use a production WSGI server instead.
# [skaffold-flask flask]  * Debug mode: off
# [skaffold-flask flask]  * Running on http://127.0.0.1:5000/ 
#                                  (Press CTRL+C to quit)
```

```bash
# 기존 pod 삭제
kubectl delete pod skaffold-flask
# pod "skaffold-flask" deleted

skaffold dev
```

```python
from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello World!2"

if __name__ == '__main__':
    print('start app')     # print문 추가 후 저장
    app.run()
```

```bash
skaffold dev
# ...
# Press Ctrl+C to exit
# [skaffold-flask flask] starting app
# [skaffold-flask flask]  * Serving Flask app "app" (lazy loading)
# [skaffold-flask flask]  * Environment: production
# [skaffold-flask flask]    WARNING: This is a development server. Do not 
#                                  use it in a production deployment.
# [skaffold-flask flask]    Use a production WSGI server instead.
# [skaffold-flask flask]  * Debug mode: off
# [skaffold-flask flask]  * Running on http://127.0.0.1:5000/ 
#                                  (Press CTRL+C to quit)
```
