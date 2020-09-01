# 3. 쿠버네티스 설치


### 3.2.2 마스터 노드 설치

```bash
sudo apt update
sudo apt install -y docker.io nfs-common dnsutils curl

# k3s 마스터 설치
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="\
    --disable traefik \
    --disable metrics-server \
    --node-name master --docker" \
    INSTALL_K3S_VERSION="v1.18.6+k3s1" sh -s -

# 마스터 통신을 위한 설정
mkdir ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown -R $(id -u):$(id -g) ~/.kube
echo "export KUBECONFIG=~/.kube/config" >> ~/.bashrc
source ~/.bashrc

# 설치 확인
kubectl cluster-info
# Kubernetes master is running at https://127.0.0.1:6443
# CoreDNS is running at https://127.0.0.1:6443/api/v1/namespaces...
# 
# To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.

kubectl get node -o wide
# NAME     STATUS   ROLES    AGE   VERSION        INTERNAL-IP    ...
# master   Ready    master   27m   v1.18.6+k3s1   10.0.1.1       ...
```

```bash
# 마스터 노드 토큰 확인
NODE_TOKEN=$(sudo cat /var/lib/rancher/k3s/server/node-token)
echo $NODE_TOKEN
# K10e6f5a983710a836b9ad21ca4a99fcxx::server:c8ae61726384c19726022879xx

MASTER_IP=$(kubectl get node master -ojsonpath="{.status.addresses[0].address}")
echo $MASTER_IP
# 10.0.1.1
```


### 3.2.3 워커 노드 추가

```bash
NODE_TOKEN=<마스터에서 확인한 토큰 입력>
MASTER_IP=<마스터에서 얻은 내부IP 입력>

sudo apt update
sudo apt install -y docker.io nfs-common curl

# k3s 워커 노드 설치
curl -sfL https://get.k3s.io | K3S_URL=https://$MASTER_IP:6443 \
    K3S_TOKEN=$NODE_TOKEN \
    INSTALL_K3S_EXEC="--node-name worker --docker" \
    INSTALL_K3S_VERSION="v1.18.6+k3s1" sh -s -
```


### 3.2.4 설치문제 해결 방법

#### 1) 마스터 노드 로그 확인

```bash
# 마스터 노드 상태 확인
sudo systemctl status k3s.service
# * k3s.service - Lightweight Kubernetes
#   ...
#   CGroup: /system.slice/k3s.service
#           └─955 /usr/local/bin/k3s server --disable traefik \
#                                           --disable metrics-server \
#                                           --node-name master \
#                                           --docker
#
# Aug 11 17:37:09 ip-10-0-1-1 k3s[955]: I0811 17:37:09.189289   ...
# Aug 11 17:37:14 ip-10-0-1-1 k3s[955]: I0811 17:37:14.190442   ...
# ...

# journald 로그 확인
sudo journalctl -u k3s.service
# Jul 13 17:51:08 ip-10-0-1-1 k3s[955]: W0713 17:51:08.168244   ...
# Jul 13 17:51:08 ip-10-0-1-1 k3s[955]: I0713 17:51:08.649295   ...
# ...
```

에러 메세지나 exception 메세지를 확인합니다.

#### 2) 워커 노드 로그 확인

```bash
# 워커 노드 상태 확인
sudo systemctl status k3s-agent.service
# * k3s-agent.service - Lightweight Kubernetes
#   ...
#   CGroup: /system.slice/k3s-agent.service
#           └─955 /usr/local/bin/k3s agent --token K10e6f5a983710 ..\
#                                          --server 10.0.1.1 \
#                                          --node-name worker \
#                                          --docker
#
# Aug 11 17:37:09 ip-10-0-1-2 k3s[955]: I0811 17:37:09.189289   ...
# Aug 11 17:37:14 ip-10-0-1-2 k3s[955]: I0811 17:37:14.190442   ...
# ...

# journald 로그 확인
sudo journalctl -u k3s-agent.service
# Jul 13 17:51:08 ip-10-0-1-2 k3s[955]: W0713 17:51:08.168244   ...
# Jul 13 17:51:08 ip-10-0-1-2 k3s[955]: I0713 17:51:08.649295   ...
# ...
```

체크리스트

- `NODE_TOKEN` 값이 제대로 설정 되었나요?
- `MASTER_IP`가 제대로 설정 되었나요?
- 워커 노드에서 마스터 노드로 IP 연결이 가능한가요?
- 마스터, 워커 노드에 적절한 포트가 열려 있나요?


#### 3) 마스터 & 워커 노드 재설치

마스터 노드에서 다음 명령을 수행하여 마스터를 제거하시기 바랍니다.

```bash
/usr/local/bin/k3s-uninstall.sh
```

워커 노드에서 다음 명령을 수행하여 워커를 제거하시기 바랍니다.

```bash
/usr/local/bin/k3s-agent-uninstall.sh
```

삭제 완료 후, 처음부터 다시 재설치를 진행합니다.


#### 4) 공식문서 참고

[https://rancher.com/docs/k3s/latest/en/installation](https://rancher.com/docs/k3s/latest/en/installation)