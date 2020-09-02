# gitops

단일 진실의 원천 예제 디렉토리입니다. GitOps 구현체인 FluxCD, ArgoCD에서 해당 디렉토리를 지속적으로 관찰하다가 새로운 YAML 정의서가 생성되거나 기존의 값이 변경될 때, 그에 따라 새롭게 배포합니다. GitOps 설정 후, 다음과 같은 리소스가 나의 클러스터에 정상적으로 배포되었는지 확인해보시기 바랍니다.

- `deployment.yaml`
- `service.yaml`

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
```


```yaml
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