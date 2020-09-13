# 13. 접근 제어

## 13.1 사용자 인증 (Authentication)

### 13.1.1 HTTP Basic Authentication

```bash
cat $HOME/.kube/config
# apiVersion: v1
# clusters:
# - cluster:
#     certificate-authority-data: LS0tLS1CRUdJTiB...g==
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
#     password: 7e92dba7..
#     username: admin
```

```bash
# 헤더 없이 접속
curl -kv https://127.0.0.1:6443/api
# HTTP/1.1 401 Unauthorized
# Www-Authenticate: Basic realm="kubernetes-master"
# {
#   "kind": "Status",
#   "apiVersion": "v1",
#   "metadata": {
#   },
#   "status": "Failure",
#   "message": "Unauthorized",
#   "reason": "Unauthorized",
#   "code": 401
# }

# basic auth 설정
curl -kv -H "Authorization: Basic $(echo -n admin:7e92dba7.. | base64)" https://127.0.0.1:6443/api
# HTTP/1.1 200 OK
# {
#   "kind": "APIVersions",
#   "versions": [
#     "v1"
#   ],
#   "serverAddressByClientCIDRs": [
#     {
#       "clientCIDR": "0.0.0.0/0",
#       "serverAddress": "172.31.17.32:6443"
#     }
#   ]
# }
```

```bash
kubectl get pod -v 7
# I0530 ...] Config loaded from file: /home/ubuntu/.kube/config
# I0530 ...] GET https://127.0.0.1:6443/.../default/pods?limit=500
# I0530 ...] Request Headers:
# I0530 ...]     Accept: application/json;as=Table;v=v1;g=...
# I0530 ...]     Authorization: Basic <masked>
```

```bash
sudo vim /var/lib/rancher/k3s/server/cred/passwd
```

```bash
# /var/lib/rancher/k3s/server/cred/passwd 

# c8ae61726384c19726022879dea9dd66,node,node,k3s:agent
# c8ae61726384c19726022879dea9dd66,server,server,k3s:server
# fcb41891d94b1a362cf7ccc4086c2465,admin,admin,system:masters
# mypassword,myuser,myuser,system:masters
```

```
# 형식은 다음과 같습니다.
password,user,uid,group1[,group2,group3]
```

```yaml
# $HOME/.kube/config
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiB...g==
    server: https://127.0.0.1:6443
  name: default
contexts:
- context:
    cluster: default
    user: default
  name: default
current-context: default
kind: Config
preferences: {}
users:
- name: default
  user:
    password: mypassword   # 비밀번호 수정
    username: myuser       # 계정이름 수정
```

```bash
# 실험용 nginx Pod 생성
kubectl run nginx --image nginx
# error: You must be logged in to the server (Unauthorized)
```

```bash
sudo systemctl restart k3s.service

# 정상적으로 Pod가 생성됩니다.
kubectl run nginx --image nginx
# pod/nginx created

# 조회도 가능합니다.
kubectl get pod
# NAME      READY   STATUS    RESTARTS   AGE
# nginx     1/1     Running   0          5s

# Pod 삭제도 가능합니다.
kubectl delete pod nginx
# pod/nginx deleted
```

### 13.1.2 X.509 인증서

```bash
wget -q --show-progress --https-only --timestamping \
  https://storage.googleapis.com/kubernetes-the-hard-way/cfssl/linux/cfssl \
  https://storage.googleapis.com/kubernetes-the-hard-way/cfssl/linux/cfssljson

chmod +x cfssl cfssljson
sudo mv cfssl cfssljson /usr/local/bin/
```

```bash
# 사용자 CSR 파일 생성
cat > client-cert-csr.json <<EOF
{
  "CN": "client-cert",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "O": "system:masters"
    }
  ]
}
EOF
```

`k3s` 쿠버네티스 CA는 다음 위치에 존재합니다.

- 인증서: `/var/lib/rancher/k3s/server/tls/client-ca.crt`
- 개인키: `/var/lib/rancher/k3s/server/tls/client-ca.key`

```bash
cat > rootCA-config.json <<EOF
{
  "signing": {
    "profiles": {
      "root-ca": {
        "usages": ["signing", "key encipherment", "client auth"],
        "expiry": "8760h"
      }
    }
  }
}
EOF
```

```bash
sudo cfssl gencert \
  -ca=/var/lib/rancher/k3s/server/tls/client-ca.crt \
  -ca-key=/var/lib/rancher/k3s/server/tls/client-ca.key \
  -config=rootCA-config.json \
  -profile=root-ca \
  client-cert-csr.json | cfssljson -bare client-cert

ls -al
# client-cert-csr.json
# client-cert-key.pem
# client-cert.csr
# client-cert.pem
# rootCA-config.json
```

```bash
kubectl config set-credentials x509 \
          --client-certificate=client-cert.pem \
          --client-key=client-cert-key.pem \
          --embed-certs=true
# User "x509" set.

kubectl config set-context default --user=x509
# Context "default" modified.

# client-certificate과 key가 base64로 인코딩되어 삽입되어 있습니다.
cat $HOME/.kube/config
# apiVersion: v1
# clusters:
# - cluster:
#     certificate-authority-data: LS0tLS1CRUdJTiB...g==
#     server: https://127.0.0.1:6443
#   name: default
# contexts:
# - context:
#     cluster: default
#     user: x509
#   name: default
# current-context: default
# kind: Config
# preferences: {}
# users:
# - name: default
#   user:
#     password: mypassword
#     username: myuser
# - name: x509
#   user:
#     client-certificate-data: LS0tLS1CRUdJTiB...
#     client-key-data: LS0tLS1CRUdJTiBSU0EgUFJ...
```

```bash
# 생성
kubectl run nginx --image nginx
# pod/nginx created

# 조회
kubectl get pod
# NAME     READY   STATUS    RESTARTS   AGE
# nginx    1/1     Running   0          5s

# 삭제
kubectl delete pod nginx
# pod/nginx deleted
```

## 13.2 역할 기반 접근 제어 (RBAC)

### 13.2.1 Role (ClusterRole)

```yaml
# role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-viewer
  namespace: default
rules:
- apiGroups: [""] # ""은 core API group을 나타냅니다.
  resources: 
  - pods
  verbs: 
  - get
  - watch
  - list
```

```bash
kubectl apply -f role.yaml
# role.rbac.authorization.k8s.io/pod-viewer created

kubectl get role
# NAME         CREATED AT
# pod-viewer   2020-05-31T17:16:47Z
```

### 13.2.2 Subjects

```bash
kubectl get serviceaccount  # 또는 sa
# NAME      SECRETS   AGE
# default   1         28h

kubectl get serviceaccount default -oyaml
# apiVersion: v1
# kind: ServiceAccount
# metadata:
#   creationTimestamp: "2020-06-07T10:08:29Z"
#   name: default
#   namespace: default
#   resourceVersion: "292"
#   selfLink: /api/v1/namespaces/default/serviceaccounts/default
#   uid: 0183509b-2e36-412d-b229-048f09b2afc1
# secrets:
# - name: default-token-vkrsk
```

```bash
kubectl create sa mysa
# serviceaccount/mysa created

kubectl get sa
# NAME      SECRETS   AGE
# default   1         28h
# mysa      1         10s
```

### 13.2.3 RoleBinding (ClusterRoleBinding)

```yaml
# read-pods.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: mysa
roleRef:
  kind: Role
  name: pod-viewer
  apiGroup: rbac.authorization.k8s.io
```

```bash
kubectl apply -f read-pods.yaml
# rolebinding.rbac.authorization.k8s.io/read-pods created

kubectl get rolebinding
# NAME        ROLE              AGE
# read-pods   Role/pod-viewer   20s
```

```yaml
# nginx-sa.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-sa
spec:
  containers:
  - image: nginx
    name: nginx
  # mysa ServiceAccount 사용
  serviceAccountName: mysa
```

```bash
kubectl apply -f nginx-sa.yaml
# pod/nginx-sa created

kubectl get pod nginx-sa -oyaml | grep serviceAccountName
#   serviceAccountName: mysa

# 내부 접근
kubectl exec -it nginx-sa -- bash
```

```bash
# kubectl 설치
$root@nginx-sa:/# curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.18.3/bin/linux/amd64/kubectl \
                 && chmod +x ./kubectl \
                 && mv ./kubectl /usr/local/bin

# Pod 리소스 조회
$root@nginx-sa:/# kubectl get pod
# NAME      READY   STATUS    RESTARTS   AGE
# nginx-sa  2/2     Running   0          2d21h

# Service 리소스 조회
$root@nginx-sa:/# kubectl get svc
# Error from server (Forbidden): services is forbidden: User 
# "system:serviceaccount:default:mysa" cannot list resource "services"
#  in API group "" in the namespace "default"
```

```bash
# Pod를 빠져나갑니다.
$root@nginx-sa:/# exit

# 호스트 서버에서 다음 명령을 수행
cat << EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-viewer
rules:
- apiGroups: [""]
  resources: 
  - pods
  - services   # services 리소스 추가
  verbs: 
  - get
  - watch
  - list
EOF
# role.rbac.authorization.k8s.io/pod-viewer edited

# 다시 Pod 접속
kubectl exec -it nginx-sa -- bash

# Service 리소스 조회
$root@nginx-sa:/# kubectl get svc
# NAME           TYPE           CLUSTER-IP      ...   
# kubernetes     ClusterIP      10.43.0.1       ...

# Pod를 빠져나갑니다.
$root@nginx-sa:/# exit
```

### Clean up

```bash
kubectl delete pod nginx-sa
kubectl delete rolebinding read-pods
kubectl delete role pod-viewer
kubectl delete sa mysa
```

## 13.3 네트워크 접근 제어 (Network Policy)

### 13.3.1 Network Policy 모듈 설치 - Canal

```bash
kubectl apply -f https://docs.projectcalico.org/manifests/canal.yaml
# configmap/canal-config created
# ...
# serviceaccount/canal created
# deployment.apps/calico-kube-controllers created
# serviceaccount/calico-kube-controllers created
```

### 13.3.2 쿠버네티스 네트워크 기본 정책

### 13.3.3 `NetworkPolicy` 문법

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-all
  namespace: default
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress: 
  - {}
  egress: 
  - {}
```

### 13.3.4 네트워크 구성

```bash
kubectl run client --image nginx
# pod/client created 
```

#### Private Zone

```yaml
# deny-all.yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: deny-all
  namespace: default
spec:
  podSelector: {}
  ingress: []
```

```bash
kubectl apply -f deny-all.yaml
# networkpolicy.networking.k8s.io/deny-all created

kubectl get networkpolicy
# NAME       POD-SELECTOR   AGE
# deny-all   <none>         2s

kubectl get networkpolicy deny-all -oyaml
# apiVersion: networking.k8s.io/v1
# kind: NetworkPolicy
# metadata:
#   ...
# spec:
#   podSelector: {}
#   policyTypes:
#   - Ingress
```

#### Web pod 오픈

```yaml
# web-open.yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: web-open
  namespace: default
spec:
  podSelector:
    matchLabels:
      run: web
  ingress:
  - from:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 80
```

```bash
kubectl apply -f web-open.yaml
# networkpolicy.networking.k8s.io/deny-all created

# run=web 이라는 라벨을 가진 웹 서버 생성
kubectl run web --image nginx
# pod/web created 

# run=non-web 이라는 라벨을 가진 웹 서버 생성
kubectl run non-web --image nginx
# pod/non-web created 

# Pod IP 확인
kubectl get pod -owide
# NAME      READY   STATUS    RESTARTS   AGE     IP            NODE 
# web       1/1     Running   0          34s     10.42.0.169   master
# non-web   1/1     Running   0          32s     10.42.0.170   master
# client    1/1     Running   0          28s     10.42.0.171   master
```

```bash
# client Pod 진입
kubectl exec -it client -- bash

# web Pod 호출
$root@client:/# curl 10.42.0.169
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...

# non-web Pod 호출
$root@client:/# curl 10.42.0.170
# curl: (7) Failed to connect to 10.42.0.170 port 80: Connection refused

$root@client:/# exit
```

#### Web과의 통신만 허용된 app

```yaml
# allow-from-web.yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: allow-from-web
  namespace: default
spec:
  podSelector:
    matchLabels:
      run: app
  ingress:
  - from:
    - podSelector:
        matchLabels:
          run: web
```

```bash
kubectl apply -f allow-from-web.yaml
# networkpolicy.networking.k8s.io/allow-from-web created

# run=app 이라는 라벨을 가진 앱 서버 생성
kubectl run app --image nginx
# pod/app created

# Pod IP 확인
kubectl get pod -owide
# NAME      READY   STATUS    RESTARTS   AGE     IP            NODE
# web       1/1     Running   0          34s     10.42.0.169   master
# non-web   1/1     Running   0          32s     10.42.0.170   master
# client    1/1     Running   0          28s     10.42.0.171   worker
# app       1/1     Running   0          28s     10.42.0.172   worker

# client Pod 진입
kubectl exec -it client -- bash

# client에서 app 서버 호출
$root@client:/# curl 10.42.0.172
# curl: (7) Failed to connect to 10.42.0.172 port 80: Connection refused

# client Pod 종료
$root@client:/# exit

# web Pod 진입
kubectl exec -it web -- bash

# web에서 app 서버 호출
$root@web:/# curl 10.42.0.172
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...

# web Pod 종료
$root@web:/# exit

# non-web Pod 진입
kubectl exec -it non-web -- bash

# non-web에서 app 서버 호출
$root@non-web:/# curl 10.42.0.172
# curl: (7) Failed to connect to 10.42.0.172 port 80: Connection refused

$root@non-web:/# exit
```

#### DB 접근 Pod

```yaml
# db-accessable.yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: db-accessable
  namespace: default
spec:
  podSelector:
    matchLabels:
      run: db
  ingress:
  - from:
    - podSelector:
        matchLabels:
          db-accessable: "true"
    ports:
    - protocol: TCP
      port: 80
```

```bash
kubectl apply -f db-accessable.yaml
# networkpolicy.networking.k8s.io/db-accessable created

# run=db 이라는 라벨을 가진 DB 생성
kubectl run db --image nginx
# pod/db created

# Pod IP 확인
kubectl get pod -owide
# NAME      READY  STATUS    RESTARTS   AGE   IP            NODE     ..
# web       1/1    Running   0          34s   10.42.0.169   master   ..
# non-web   1/1    Running   0          32s   10.42.0.170   master   ..
# client    1/1    Running   0          28s   10.42.0.171   worker   ..
# app       1/1    Running   0          28s   10.42.0.172   worker   ..
# db        1/1    Running   0          28s   10.42.0.173   worker   ..

# app Pod 진입
kubectl exec -it app -- bash

# db로 연결 확인
$root@app:/# curl 10.42.0.173
# curl: (7) Failed to connect to 10.42.0.173 port 80: Connection refused

# app Pod 종료
$root@app:/# exit

# db-accessable=true 라벨 추가
kubectl label pod app db-accessable=true
# pod/app labeled

# app Pod 진입
kubectl exec -it app -- bash

# db로 연결 확인
$root@app:/# curl 10.42.0.173
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...

$root@app:/# exit
```

#### DMZ zone 연결

```yaml
# allow-dmz.yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: allow-dmz
  namespace: default
spec:
  podSelector:
    matchLabels:
      run: web
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          zone: dmz
    ports:
    - protocol: TCP
      port: 80
```

```bash
kubectl delete networkpolicy web-open
# networkpolicy.networking.k8s.io/web-open deleted

kubectl create ns dmz
# namespace/dmz created

kubectl label namespace dmz zone=dmz
# namespace/dmz labeld
```

```bash
kubectl apply -f allow-dmz.yaml
# networkpolicy.networking.k8s.io/allow-dmz created

# DMZ 네임스페이스 Proxy 서버 생성
kubectl run proxy --image nginx -n dmz
# pod/proxy created

# dmz 네임스페이스 Pod 조회
kubectl get pod -owide -n dmz
# NAME      READY   STATUS    RESTARTS   AGE     IP            NODE 
# proxy     1/1     Running   0          34s     10.42.0.183   master

# proxy Pod 진입
kubectl exec -it proxy -n dmz -- bash

# dmz 네임스페이스에 있는 proxy 서버에서는 web 서버로 통신이 잘 됩니다.
$root@proxy:/# curl 10.42.0.169   # 웹서버 IP
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...

# proxy Pod 종료
$root@proxy:/# exit

# default 네임스페이스의 client Pod로 들어가서 다시 web 서버로 호출합니다.
kubectl exec -it client -- bash

# web 서버로 호출
$root@client:/# curl 10.42.0.169
# curl: (7) Failed to connect to 10.42.0.169 port 80: Connection refused

$root@client:/# exit
```

### 13.3.5 네트워크 구성 - Egress

#### dev 네임스페이스 외의 아웃바운드 차단

```yaml
# dont-leave-dev.yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: dont-leave-dev
  namespace: dev
spec:
  podSelector: {}
  egress:
  - to:
    - podSelector: {}
```

```bash
# dev 네임스페이스 생성
kubectl create ns dev
# namespace/dev created

# Egress 네트워크 정책 생성
kubectl apply -f dont-leave-dev.yaml
# networkpolicy.networking.k8s.io/dont-leave-dev created

kubectl run dev1 --image nginx -n dev
# pod/dev1 created

kubectl run dev2 --image nginx -n dev
# pod/dev2 created

# Pod IP 확인
kubectl get pod -owide -n dev
# NAME      READY   STATUS    RESTARTS   AGE     IP            NODE 
# dev1      1/1     Running   0          34s     10.42.0.191   master 
# dev2      1/1     Running   0          32s     10.42.0.192   master 

# dev1 Pod 진입
kubectl exec -it dev1 -n dev -- bash

# dev1에서 dev2로 호출
$root@dev1:/# curl 10.42.0.192
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...

# dev1에서 proxy 서버로 호출 (proxy 서버IP: 10.42.0.183)
$root@dev1:/# curl 10.42.0.183
# curl: (7) Failed to connect to 10.42.0.183 port 80: Connection refused

$root@dev1:/# exit
```

#### Metadata API 접근 금지

```bash
# instance id 확인
curl 169.254.169.254/1.0/meta-data/instance-id
# i-0381e52ee2cxxx
```

```yaml
# block-metadata.yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: block-metadata
  namespace: default
spec:
  podSelector: {}
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 169.254.169.254/32
```

```bash
# client Pod 진입
kubectl exec -it client -- bash

# IP를 이용하여 metadata를 확인할 수 있습니다.
$root@client:/# curl 169.254.169.254/1.0/meta-data/instance-id
# i-0381e52ee2cxxx

# client Pod 종료
$root@client:/# exit

# IP 대역 차단 네트워크 정책을 생성합니다.
kubectl apply -f block-metadata.yaml
# networkpolicy.networking.k8s.io/block-metadata created

# client Pod 진입
kubectl exec -it client -- bash

# 동일한 명령에 대해서 연결이 막혔습니다.
$root@client:/# curl 169.254.169.254/1.0/meta-data/instance-id
# curl: (7) Failed to connect to 169.254.169.254 port 80: Connection refused
```

### 13.3.6 `AND` & `OR` 조건 비교

#### `AND` 조건

```yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: and-condition
  namespace: default
spec:
  podSelector:
    matchLabels:
      run: web
  ingress:
  - from:
    - podSelector:
        matchLabels:
          shape: circle
    - podSelector:
        matchLabels:
          color: red
```

#### `OR` 조건

```yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: or-condition
  namespace: default
spec:
  podSelector:
    matchLabels:
      run: web
  ingress:
  - from:
    - podSelector:
        matchLabels:
          shape: circle
  - from:
    - podSelector:
        matchLabels:
          color: red
```

### 13.3.7 네트워크 정책 전체 스펙

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: full-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - ipBlock:
        cidr: 172.17.0.0/16
        except:
        - 172.17.1.0/24
    - namespaceSelector:
        matchLabels:
          project: dev
    - podSelector:
        matchLabels:
          role: web
    ports:
    - protocol: TCP
      port: 3306
  egress:
  - to:
    - ipBlock:
        cidr: 10.0.0.0/24
    ports:
    - protocol: TCP
      port: 53
```

### Clean up

```bash
kubectl delete pod --all
kubectl delete networkpolicy --all -A
kubectl delete ns dmz
kubectl delete ns dev
```
