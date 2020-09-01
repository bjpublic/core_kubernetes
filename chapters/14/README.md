# 14. 로깅과 모니터링

## 14.1 로깅 시스템 구축

### 14.1.2 클러스터 레벨 로깅 원리

```bash
docker logs <CONTAINER_ID>
```

```bash
/var/lib/docker/containers/<CONTAINER_ID>/<CONTAINER_ID>-json.log
```

```bash
# nginx라는 컨테이너를 하나 실행하고 CONTAINER_ID 값을 복사합니다.
docker run -d nginx
# 4373b7e095215c23057b1dc4423527239e56a33dbd

# docker 명령을 통한 로그 확인
docker logs 4373b7e095215c23057b1dc4423527239e56a33dbd
# /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will ...
# /docker-entrypoint.sh: Looking for shell scripts in /docker-...
# /docker-entrypoint.sh: Launching /docker-entrypoint.d/...
# ...

# 호스트 서버의 로그 파일 확인
sudo tail /var/lib/docker/containers/4373b7e095215c23057b1dc4423527239e56a33dbd/4373b7e095215c23057b1dc4423527239e56a33dbd-json.log
# {"log":"/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, \
# will attempt to perform configuration\n","stream":"stdout",\
# "time":"2020-07-11T03:22:11.817939191Z"}
# ...

# 컨테이너 정리
docker stop 4373b7e095215c23057b1dc4423527239e56a33dbd
docker rm 4373b7e095215c23057b1dc4423527239e56a33dbd
```

### 14.1.6 EFK Stack

```bash
# fetch stable repository의 elastic-stack
helm fetch --untar stable/elastic-stack --version 2.0.1

vim elastic-stack/values.yaml
```

```yaml
# elastic-stack/values.yaml

# 약 12줄
logstash:
  enabled: false  # 기존 true

# 약 29줄
fluent-bit:
  enabled: true   # 기존 false
```

```bash
# elasticsearch 수정
vim elastic-stack/charts/elasticsearch/values.yaml
```

```yaml
# elastic-stack/charts/elasticsearch/values.yaml
# ...
# 약 110줄
client:
  replicas: 1  # 기존 2
# ...
# 약 171줄
master:
  replicas: 2  # 기존 3
# ...
# 약 225줄
data:
  replicas: 1  # 기존 2
```

```bash
# fluent-bit 수정
vim elastic-stack/charts/fluent-bit/values.yaml
```

```yaml
# elastic-stack/charts/fluent-bit/values.yaml
# ...
# 약 45줄
backend:
  type: es    # 기존 forward
  # ...
  es:
    host: efk-elasticsearch-client   # 기존 elasticsearch -> host 변경

# ...

# 약 226줄
input:
  tail:
    memBufLimit: 5MB
    parser: docker
    path: /var/log/containers/*.log
    ignore_older: ""
  systemd:
    enabled: true   # 기존 false
    filters:
      systemdUnit:
        - docker.service
        - k3.service    # 기존 kubelet.service
        # - node-problem-detector.service  --> 주석처리
```

```bash
# kibana ingress 수정
vim elastic-stack/charts/kibana/values.yaml
```

```yaml
# elastic-stack/charts/kibana/values.yaml
# ...
# 약 79줄 - kibana ingress 설정하기
ingress:
  enabled: true   # 기존 false
  hosts:
  - kibana.10.0.1.1.sslip.io   # 공인IP 입력
  annotations:
    kubernetes.io/ingress.class: nginx
```

```bash
helm install efk ./elastic-stack
# NAME: efk
# LAST DEPLOYED: Sat Jul 11 07:17:06 2020
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# NOTES:
# The elasticsearch cluster and associated extras have been installed.
# Kibana can be accessed:
# ...

# 모든 Pod가 다 실행되기까지 wait
watch kubectl get pod,svc
```

index를 생성하는 방법은 다음과 같습니다.

1. `Explore on my own` 클릭
2. 왼쪽 패널 `Discover` 클릭
3. Index pattern에 `kubernetes_cluster-*` 입력 > Next step
4. Time Filter field name에 `@timestamp` 선택 > Create index pattern
5. 다시 `Discover` 패널로 가면 `Pod`들의 로그들을 볼 수 있습니다.

### Clean up

```bash
helm delete efk
```

## 14.2 리소스 모니터링 시스템 구축

### 14.2.2 컨테이너 메트릭 정보 수집 원리

```bash
docker run -d nginx
# 4373b7e095215c23057b1dc4423527239e56a33dbd

docker stats 4373b7e095215c23057b1dc4423527239e56a33dbd
# CONTAINER ID    NAME     CPU %     MEM USAGE / LIMIT     MEM    ...    
# 4af9f73eb06f    dreamy   0.00%     3.227MiB / 7.773GiB   0.04%  ...

docker stop 4373b7e095215c23057b1dc4423527239e56a33dbd
docker rm 4373b7e095215c23057b1dc4423527239e56a33dbd
```

### 14.2.3 Prometheus & Grafana 구축

```bash
helm fetch --untar stable/prometheus-operator --version 8.16.1

vim prometheus-operator/values.yaml
```

```yaml
# 약 495줄 - grafana ingress 설정하기
grafana:
  ...
  ingress:
    enabled: true   # 기존 false
    annotations:
      kubernetes.io/ingress.class: nginx   # 추가
    hosts:
    - grafana.10.0.1.1.sslip.io            # 공인IP 입력
```

```bash
helm install mon ./prometheus-operator
# manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
# manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
# manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
# manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
# manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
# manifest_sorter.go:192: info: skipping unknown hook: "crd-install"
# NAME: mon
# LAST DEPLOYED: Thu Jul 16 08:44:38 2020
# ...

watch kubectl get pod
```

웹 브라우저를 통해 grafana를 접근합니다.

- `username`: admin
- `password`: prom-operator

좌측 상단의 `Home`을 누르면 다양한 대시보드가 생성된 것을 볼 수 있습니다.

### Clean up

```bash
helm delete mon
```
