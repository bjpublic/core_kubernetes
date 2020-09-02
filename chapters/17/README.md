# 17. 워크플로우 관리

## 17.1 Argo workflow 소개

### 17.1.4 설치

```bash
kubectl create namespace argo
# namespace/argo created

# Workflow CRD 및 Argo controller 설치
kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo/v2.8.1/manifests/install.yaml
# customresourcedefinition.apiextensions.k8s.io/clusterworkflowtemplates.argoproj.io created
# customresourcedefinition.apiextensions.k8s.io/cronworkflows.argoproj.io created
# customresourcedefinition.apiextensions.k8s.io/workflows.argoproj.io created
# ...

# default 서비스계정에 admin 권한 부여
kubectl create rolebinding default-admin --clusterrole=admin \
      --serviceaccount=default:default
# rolebinding.rbac.authorization.k8s.io/default-admin created

# ingress 설정
cat << EOF | kubectl apply -f -
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
  name: argo-server
  namespace: argo
spec:
  rules:
  - host: argo.10.0.1.1.sslip.io
    http:
      paths:
      - backend:
          serviceName: argo-server
          servicePort: 2746
        path: /
EOF
```

- `SUBMIT NEW WORKFLOW` 클릭
- `SUBMIT` 클릭
- 노란색 (혹은 파란색) Workflow 클릭 (예제 이름: `fantastic-tiger`)
- `YAML`과 `LOGS` 클릭하여 Workflow 정보 확인

```bash
kubectl get workflow  # wf
# NAME              STATUS      AGE
# fantastic-tiger   Succeeded   10m

kubectl describe workflow fantastic-tiger
# ...
```

## 17.2 Workflow 구성하기

### 17.2.1 단일 Job 실행

```yaml
# single-job.yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
  namespace: default
spec:
  entrypoint: whalesay
  templates:
  - name: whalesay
    container:
      image: docker/whalesay
      command: [cowsay]
      args: ["hello world"]
      resources:
        limits:
          memory: 32Mi
          cpu: 100m
```

```bash
# Workflow 생성
kubectl create -f single-job.yaml
# workflow.argoproj.io/hello-world-tcnjj created

kubectl get wf
# NAME                STATUS      AGE
# wonderful-dragon    Succeeded   8m21s
# hello-world-tcnjj   Succeeded   17s

kubectl get pod
# NAME                READY   STATUS      RESTARTS   AGE
# wonderful-dragon    0/2     Completed   0          8m34s
# hello-world-tcnjj   0/2     Completed   0          31s

kubectl logs hello-world-tcnjj -c main
#  _____________
# < hello world >
#  -------------
#     \
#      \
#       \
#                     ##        .
#               ## ## ##       ==
#            ## ## ## ##      ===
#        /""""""""""""""""___/ ===
#   ~~~ {~~ ~~~~ ~~~ ~~~~ ~~ ~ /  ===- ~~~
#        \______ o          __/
#         \    \        __/
#           \____\______/
# 
# 
# Hello from Docker!
# This message shows that your installation appears to be working 
```

### 17.2.2 파라미터 전달

```yaml
# param.yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-parameters-
  namespace: default
spec:
  entrypoint: whalesay
  arguments:
    parameters:
    - name: message
      value: hello world through param

  templates:
  ###############
  # entrypoint
  ###############
  - name: whalesay
    inputs:
      parameters:
      - name: message
    container:
      image: docker/whalesay
      command: [cowsay]
      args: ["{{inputs.parameters.message}}"]
```

### 17.2.3 Serial step 실행

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: serial-step-
  namespace: default
spec:
  entrypoint: hello-step
  templates:

  ###############
  # template job
  ###############
  - name: whalesay
    inputs:
      parameters:
      - name: message
    container:
      image: docker/whalesay
      command: [cowsay]
      args: ["{{inputs.parameters.message}}"]

  ###############
  # entrypoint
  ###############
  - name: hello-step
    # 순차 실행
    steps:
    - - name: hello1
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "hello1"
    - - name: hello2
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "hello2"
    - - name: hello3
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "hello3"
```

### 17.2.4 Parallel step 실행

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: parallel-steps-
  namespace: default
spec:
  entrypoint: hello-step
  templates:

  ###############
  # template job
  ###############
  - name: whalesay
    inputs:
      parameters:
      - name: message
    container:
      image: docker/whalesay
      command: [cowsay]
      args: ["{{inputs.parameters.message}}"]

  ###############
  # entrypoint
  ###############
  - name: hello-step
    # 병렬 실행
    steps:
    - - name: hello1
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "hello1"
    - - name: hello2
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "hello2"
      - name: hello3        # 기존 double dash에서 single dash로 변경
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "hello3"
```

### 17.2.5 복잡한 DAG 실행

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: dag-diamond-
  namespace: default
spec:
  entrypoint: diamond
  templates:
  
  ###############
  # template job
  ###############
  - name: echo
    inputs:
      parameters:
      - name: message
    container:
      image: alpine:3.7
      command: [echo, "{{inputs.parameters.message}}"]

  ###############
  # entrypoint
  ###############
  - name: diamond
    # DAG 구성
    dag:
      tasks:
      - name: A
        template: echo
        arguments:
          parameters: [{name: message, value: A}]
      - name: B
        dependencies: [A]
        template: echo
        arguments:
          parameters: [{name: message, value: B}]
      - name: C
        dependencies: [A]
        template: echo
        arguments:
          parameters: [{name: message, value: C}]
      - name: D
        dependencies: [B, C]
        template: echo
        arguments:
          parameters: [{name: message, value: D}]
```

### 17.2.6 종료 핸들링

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: error-handlers-
  namespace: default
spec:
  entrypoint: intentional-fail
  # 에러 핸들러 작업 지정
  onExit: error-handler

  templates:
  
  ###############
  # template job
  ###############
  - name: send-email
    container:
      image: alpine:latest
      command: [sh, -c]
      args: ["echo send e-mail: {{workflow.name}} {{workflow.status}}"]
  
  ###############
  # 종료 핸들러
  ###############
  - name: error-handler
    steps:
    - - name: notify
        template: send-email

  ###############
  # entrypoint
  ###############
  - name: intentional-fail
    container:
      image: alpine:latest
      command: [sh, -c]
      args: ["echo intentional failure; exit 1"]
```

### Clean up

```bash
kubectl delete wf --all
kubectl delete -n argo -f https://raw.githubusercontent.com/argoproj/argo/v2.8.1/manifests/install.yaml
```
