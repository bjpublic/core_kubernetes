# 9. Ingress 리소스

## 9.1 Ingress란

### 9.1.2 NGINX Ingress Controller 설치

```bash
# NGINX Ingress Controller를 위한 네임스페이스를 생성합니다.
kubectl create ns ctrl
# namespace/ctrl created

# nginx-ingress 설치
helm install ingress stable/nginx-ingress --version 1.40.3 -n ctrl
# NAME: ingress
# LAST DEPLOYED: Wed Mar 11 13:31:14 2020
# NAMESPACE: ctrl
# STATUS: deployed
# REVISION: 1
# TEST SUITE: None
# NOTES:
#     ...
```

```bash
kubectl get pod -n ctrl
# NAME                            READY   STATUS      RESTARTS  AGE
# ingress-controller-7444984      1/1     Running     0         6s
# svclb-ingress-controller-dcph4  2/2     Running     0         6s
# ingress-default-backend-659bd6  1/1     Running     0         6s
 
kubectl get svc -n ctrl
# NAME                     TYPE          ...  EXTERNAL-IP    PORT(S)  
# ingress-default-backend  ClusterIP     ...  <none>         80/TCP
# ingress-controller       LoadBalancer  ...  10.0.1.1       80:..,443:..
```

## 9.2 `Ingress` 기본 사용법

### 9.2.1 도메인 주소 테스트

[https://sslip.io](https://sslip.io)의 서브 도메인에 IP를 입력하면 해당하는 IP를 DNS lookup 결과로 반환해 줍니다.

```
IP == IP.sslip.io
```

```bash
nslookup 10.0.1.1.sslip.io
# Address: 10.0.1.1
```

```bash
nslookup subdomain.10.0.1.1.sslip.io
# Address: 10.0.1.1
```

#### Ingress Controller IP 확인 방법 

다음 명령을 통해 Ingress Controller IP를 확인할 수 있습니다. 호스트 서버(마스터, 워커) 중 하나의 내부IP가 반환될 것입니다.

```bash
INGRESS_IP=$(kubectl get svc -nctrl ingress-nginx-ingress-controller -ojsonpath="{.status.loadBalancer.ingress[0].ip}")
echo $INGRESS_IP
# 10.0.1.1
```


### 9.2.2 첫 `Ingress` 생성

```bash
kubectl run mynginx --image nginx --expose --port 80
# pod/mynginx created
# pod/service created

# comma로 여러 리소스를 한번에 조회할 수 있습니다.
kubectl get pod,svc mynginx
# NAME          READY   STATUS    RESTARTS   AGE
# pod/mynginx   1/1     Running   0          8m38s

# NAME             TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
# service/mynginx  ClusterIP  10.43.203.151  <none>        80/TCP    8m38s
```

```yaml
# mynginx-ingress.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
  name: mynginx
spec:
  rules:
  - host: 10.0.1.1.sslip.io
    http:
      paths:
      - path: /
        backend:
          serviceName: mynginx
          servicePort: 80
```

```bash
kubectl apply -f mynginx-ingress.yaml
# ingress.extensions/mynginx created

kubectl get ingress
# NAME      CLASS    HOSTS              ADDRESS    PORTS     AGE
# mynginx   <none>   10.0.1.1.sslip.io  10.0.1.1   80        10m

# mynginx 서비스로 연결
curl 10.0.1.1.sslip.io
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...
```

### 9.2.3 도메인 기반 라우팅

```bash
# apache web server
kubectl run apache --image httpd --expose --port 80
# pod/apache created
# service/apache created

# nginx web server
kubectl run nginx --image nginx --expose --port 80
# pod/nginx created
# service/nginx created
```

```yaml
# domain-based-ingress.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
  name: apache-domain
spec:
  rules:
    # apache 서브 도메인
  - host: apache.10.0.1.1.sslip.io
    http:
      paths:
      - backend:
          serviceName: apache
          servicePort: 80
        path: /
---  
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
  name: nginx-domain
spec:
  rules:
    # nginx 서브 도메인
  - host: nginx.10.0.1.1.sslip.io
    http:
      paths:
      - backend:
          serviceName: nginx
          servicePort: 80
        path: /
```

```bash
kubectl apply -f domain-based-ingress.yaml
# ingress.extensions/apache-domain created
# ingress.extensions/nginx-domain created

curl apache.10.0.1.1.sslip.io
# <html><body><h1>It works!</h1></body></html>

curl nginx.10.0.1.1.sslip.io
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...
```

### 9.2.4 Path 기반 라우팅

```yaml
# path-based-ingress.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: / 
  name: apache-path
spec:
  rules:
  - host: 10.0.1.1.sslip.io
    http:
      paths:
      - backend:
          serviceName: apache
          servicePort: 80
        path: /apache
---  
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: / 
  name: nginx-path
spec:
  rules:
  - host: 10.0.1.1.sslip.io
    http:
      paths:
      - backend:
          serviceName: nginx
          servicePort: 80
        path: /nginx
```

```bash
kubectl apply -f path-based-ingress.yaml
# ingress.extensions/apache-path created
# ingress.extensions/nginx-path created

curl 10.0.1.1.sslip.io/apache
# <html><body><h1>It works!</h1></body></html>

curl 10.0.1.1.sslip.io/nginx
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...
```

## 9.3 Basic Auth 설정

### 9.3.1 Basic Authentication

```bash
Authorization: Basic $BASE64(user:password)
```

```bash
# 헤더 없이 접속 시도
curl -v https://httpbin.org/basic-auth/foo/bar
# HTTP/2 401 
# ...
# www-authenticate: Basic realm="Fake Realm"

# basic auth 헤더 전송
curl -v -H "Authorization: Basic $(echo -n foo:bar | base64)" https://httpbin.org/basic-auth/foo/bar
# HTTP/2 200 
# ..
# {
#   "authenticated": true, 
#   "user": "foo"
# }
```

### 9.3.2 Basic Auth 설정

```bash
# htpasswd binary 설치
sudo apt install -y apache2-utils

# 아이디는 foo, 비밀번호는 bar인 auth 파일 생성
htpasswd -cb auth foo bar

# 생성한 auth 파일을 Secret으로 생성합니다.
kubectl create secret generic basic-auth --from-file=auth

# Secret 리소스 생성 확인
kubectl get secret basic-auth -oyaml
# apiVersion: v1
# data:
#   auth: Zm9vOiRhcHIxJE1UTy9MMUN0JEdNek8xOVZtMXdKYWt6R0tjLjhQTS8K
# kind: Secret
# metadata:
#   name: basic-auth
#   namespace: default
#   resourceVersion: "3648288"
#   selfLink: /api/v1/namespaces/default/secrets/basic-auth
#   uid: b9966176-5259-4e3f-8476-c7e308ae21a1
# type: Opaque
```

```yaml
# apache-auth.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    nginx.ingress.kubernetes.io/auth-realm: 'Authentication Required - foo'
  name: apache-auth
spec:
  rules:
  - host: apache-auth.10.0.1.1.sslip.io
    http:
      paths:
      - backend:
          serviceName: apache
          servicePort: 80
        path: /
```

```bash
curl -I apache-auth.10.0.1.1.sslip.io
# HTTP/1.1 401 Unauthorized
# Server: nginx/1.17.10
# Date: Tue, 07 Jul 2020 12:30:43 GMT
# Content-Type: text/html
# Content-Length: 180
# Connection: keep-alive
# WWW-Authenticate: Basic realm="Authentication Required - foo"

curl -I -H "Authorization: Basic $(echo -n foo:bar | base64)" apache-auth.10.0.1.1.sslip.io
# HTTP/1.1 200 OK
# Server: nginx/1.17.10
# Date: Tue, 07 Jul 2020 12:31:14 GMT
# Content-Type: text/html
# Content-Length: 45
# Connection: keep-alive
# Last-Modified: Mon, 11 Jun 2007 18:53:14 GMT
# ETag: "2d-432a5e4a73a80"
# Accept-Ranges: bytes
```

## 9.4 TLS 설정

### 9.4.1 Self-signed 인증서 설정

#### Self-signed 인증서 생성하기

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=apache-tls.10.0.1.1.sslip.io"
# Generating a RSA private key
# ...................................................+++++
# .....+++++
# writing new private key to 'tls.key'
# -----
tls.crt  # 인증서
tls.key  # 개인키
```

```bash
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: my-tls-certs
  namespace: default
data:
  tls.crt: $(cat tls.crt | base64 | tr -d '\n')
  tls.key: $(cat tls.key | base64 | tr -d '\n')
type: kubernetes.io/tls
EOF
```

#### Ingress TLS 설정하기

```yaml
# apache-tls.yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: apache-tls
spec:
  tls:
  - hosts:
      - apache-tls.10.0.1.1.sslip.io
    secretName: my-tls-certs
  rules:
  - host: apache-tls.10.0.1.1.sslip.io
    http:
      paths:
      - path: /
        backend:
          serviceName: apache
          servicePort: 80
```

```bash
kubectl apply -f apache-tls.yaml
# ingress.networking.k8s.io/apache-tls created
```

### 9.4.2 cert-manager를 이용한 인증서 발급 자동화

#### cert-manager 설치

```bash
# cert-manager라는 네임스페이스 생성
kubectl create namespace cert-manager

# cert-manager 관련 사용자 정의 리소스 생성
kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v0.15.1/cert-manager.crds.yaml
# customresourcedefinition.apiextensions.k8s.io/issuers.cert-manager.io created
# customresourcedefinition.apiextensions.k8s.io/orders.acme.cert-manage...
# ...

# jetstack 레포지토리 추가
helm repo add jetstack https://charts.jetstack.io
#"jetstack" has been added to your repositories

# 레포지토리 index 업데이트
helm repo update
# Hang tight while we grab the latest from your chart repositories...
# ...Successfully got an update from the "jetstack" chart repository

# cert-manager 설치
helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v0.15.1
```

#### Issuer 생성

```yaml
# http-issuer.yaml
apiVersion: cert-manager.io/v1alpha2
kind: ClusterIssuer
metadata:
  name: http-issuer
spec:
  acme:
    email: <EMAIL>
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: issuer-key
    solvers:
    - http01:
       ingress:
         class: nginx
```

```bash
kubectl apply -f http-issuer.yaml
# clusterissuer.cert-manager.io/http-issuer created

kubectl get clusterissuer
# NAME          READY   AGE
# http-issuer   True    2m
```

#### cert-manager가 관리하는 TLS `Ingress` 생성

```yaml
# apache-tls-issuer.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
    # 앞서 생성한 발급자 지정
    cert-manager.io/cluster-issuer: http-issuer
  name: apache-tls-issuer
spec:
  rules:
  # 10.0.1.1을 공인IP로 변경해 주세요.
  - host: apache-issuer.10.0.1.1.sslip.io
    http:
      paths:
      - backend:
          serviceName: apache
          servicePort: 80
        path: /
  tls:
  - hosts:
    # 10.0.1.1을 공인IP로 변경해 주세요.
    - apache-issuer.10.0.1.1.sslip.io
    secretName: apache-tls
```

```bash
kubectl apply -f apache-tls-issuer
# ingress.networking.k8s.io/apache-tls-issuer created

kubectl get certificate 
# NAME         READY   SECRET       AGE
# apache-tls   False   apache-tls   38s

kubectl get certificate 
# NAME         READY   SECRET       AGE
# apache-tls   True    apache-tls   75s
```

### Clean up

```bash
kubectl delete ingress --all
kubectl delete pod apache nginx mynginx
kubectl delete svc apache nginx mynginx
```
