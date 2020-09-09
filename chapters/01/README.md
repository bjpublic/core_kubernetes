# 1. 도커기초

## 1.1 도커 소개

### 1.1.3 도커 설치

```bash
sudo apt update && sudo apt install -y docker.io net-tools
sudo usermod -aG docker $USER

# 서버를 재시작합니다.
sudo reboot
```


## 1.2 도커 기본 명령

### 1.2.1 컨테이너 실행

```bash
sudo apt install -y cowsay
cowsay hello world!
#  ______________
# < hello world! >
#  --------------
#         \   ^__^
#          \  (oo)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||
# 
```

```bash
docker run docker/whalesay cowsay 'hello world!'
# Unable to find image 'docker/whalesay:latest' locally
# latest: Pulling from docker/whalesay
# 23cwc732thk4: Pull complete
# t4nb4f93jc42: Pull complete
# ...
#  ______________
# < hello world! >
#  --------------
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
```

```bash
docker run docker/whalesay echo hello
# hello
```

```bash
# `-d` 옵션 추가
docker run -d nginx
# Unable to find image 'nginx:latest' locally
# latest: Pulling from library/nginx
# 5e6ec7f28fb7: Pull complete
# ab804f9bbcbe: Pull complete
# ...
# d7455a395f1a4745974b0be1372ea58c1499f52f97d96b48f92eb8fa765bc69f
```


### 1.2.2 컨테이너 조회

```bash
docker ps
```

### 1.2.3 컨테이너 상세 정보 확인

```bash
# docker ps를 통해 얻은 <CONTAINER_ID>로 상세 정보 확인
docker inspect d7455a395f1a
# [
#   {
#     "Id": "d7455a395f1a0f562af7a0878397953331b791c229a31b7eba0",
#     "Created": "2020-07-12T05:26:23.554118194Z",
#     "Path": "/",
#     "Args": [
#     ],
#     "State": {
#       "Status": "running",
#       "Running": true,
#       "Paused": false,
#       ...
```

### 1.2.4 컨테이너 로깅

```bash
docker logs -f d7455a395f1a
# /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, ...
# /docker-entrypoint.sh: Looking for shell scripts in ...
# ...
```

`<CTRL>+<C>`로 로깅을 종료

### 1.2.5 컨테이너 명령전달

```bash
# 새로운 패키지 설치
docker exec d7455a395f1a sh -c 'apt update && apt install -y wget'
docker exec d7455a395f1a wget localhost
# ..
# Saving to: 'index.html'
#      0K .......... ..           166M=0s
# 2020-07-16 15:15:43 (166 MB/s) - 'index.html' saved [13134]
```

### 1.2.6 컨테이너 / 호스트간 파일 복사

```bash
# 호스트에서 컨테이너로 파일 복사
docker cp /etc/passwd d7455a395f1a:/usr/share/nginx/html/.

# 확인
docker exec d7455a395f1a curl -s localhost/passwd
# root:x:0:0:root:/root:/bin/bash
# daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
# bin:x:2:2:bin:/bin:/usr/sbin/nologin
# ...

# 반대로 컨테이너에서 호스트로 파일 복사
docker cp d7455a395f1a:/usr/share/nginx/html/index.html .

# 확인
cat index.html
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...
```

### 1.2.7 컨테이너 중단

```bash
docker stop d7455a395f1a
# d7455a395f1a

docker ps
# CONTAINER ID    IMAGE   COMMAND   CREATED   STATUS   PORTS    NAMES

docker ps -a
# CONTAINER ID   IMAGE  COMMAND       ...  STATUS       PORTS   NAMES
# d7455a395f1a   nginx  "/docker..."  ...  Exited (0)           ...
# ...
```

### 1.2.8 컨테이너 재개

```bash
docker start d7455a395f1a
# d7455a395f1a

docker ps
# CONTAINER ID    IMAGE    COMMAND                  CREATED         ...
# d7455a395f1a    nginx    "/docker-entrypoint.."   4 minutes ago   ...
```

### 1.2.9 컨테이너 삭제

```bash
# 컨테이너 중단
docker stop d7455a395f1a
# d7455a395f1a

# 컨테이너 삭제
docker rm d7455a395f1a
# d7455a395f1a

# 컨테이너 조회, nginx가 사라졌습니다.
docker ps -a
# CONTAINER ID  IMAGE            COMMAND       ...  STATUS      ...
# fc47859c2fdc  docker/whalesay  "echo hello"  ...  Exited (0)  ...
# 32047a546124  docker/whalesay  "cowsay ..."  ...  Exited (0)  ...
```

### 1.2.10 Interactive 컨테이너

```bash
docker run -it ubuntu:16.04 bash
# Unable to find image 'ubuntu:16.04' locally

# 컨테이너 내부
$root@1c23d59f4289:/#

$root@1c23d59f4289:/# cat /etc/os-release
# NAME="Ubuntu"
# VERSION="16.04.6 LTS (Xenial Xerus)"
# ID=ubuntu
# ID_LIKE=debian

# 컨테이너에서 빠져 나오기
$root@1c23d59f4289:/# exit
```

```bash
# 컨테이너 실행
docker run -d nginx
# c4484sc501e9a

# exec 명령을 통해서 bash 접속
docker exec -it c4484c501e9a bash

# 컨테이너 내부
$root@c4484c501e9a:/#
```


## 1.3 도커 저장소

### 1.3.2 이미지 tag 달기

```bash
docker tag nginx:latest <USERNAME>/nginx:1
```


### 1.3.3 이미지 확인

```bash
docker images
# REPOSITORY         TAG        IMAGE ID        CREATED          SIZE
# nginx              latest     89b0e8f41524    2 minutes ago    150MB
# hongkunyoo/nginx   latest     89b0e8f41524    2 minutes ago    150MB
# hongkunyoo/nginx   1          89b0e8f41524    2 minutes ago    150MB
# ubuntu             16.04      330ae480cb85    8 days ago       125MB
# docker/whalesay    latest     6b362a9f73eb    5 years ago      247MB
```

### 1.3.4 도커허브 로그인

```bash
docker login
# Username: <USERNAME>
# Password: ****
# WARNING! Your password will be stored unencrypted in ...
# Configure a credential helper to remove this warning. See
# https://docs.docker.com/engine/reference/commandline/login/#credentials-store

# Login Succeeded
```

### 1.3.5 이미지 업로드

```bash
docker push <USERNAME>/nginx
# The push refers to repository [docker.io/hongkunyoo/nginx]
# f978b9ed3f26: Preparing
# 9040af41bb66: Preparing
```

### 1.3.6 이미지 다운로드

```bash
docker pull redis
# Using default tag: latest
# latest: Pulling from library/redis
# ...
# 85a6a5c53ff0: Pull complete

docker images
# REPOSITORY         TAG         IMAGE ID        CREATED          SIZE
# hongkunyoo/nginx   latest      89b0e8f41524    2 minutes ago    150MB
# hongkunyoo/nginx   1           89b0e8f41524    2 minutes ago    150MB
# nginx              latest      89b0e8f41524    2 minutes ago    150MB
# redis              latest      235592615444    3 weeks ago      104MB
# ubuntu             16.04      330ae480cb85    8 days ago       125MB
# docker/whalesay    latest      6b362a9f73eb    5 years ago      247MB
```

### 1.3.7 이미지 삭제

```bash
docker rmi redis
# Untagged: redis:latest
# Untagged: redis@sha256:800f2587bf3376cb01e6307afe599ddce9439deafbd...
# Deleted: sha256:2355926154447ec75b25666ff5df14d1ab54f8bb4abf731be2fcb818c7a7f145

docker images
# REPOSITORY         TAG       IMAGE ID         CREATED          SIZE
# nginx              latest    89b0e8f41524     2 minutes ago    150MB
# hongkunyoo/nginx   latest    89b0e8f41524     2 minutes ago    150MB
# hongkunyoo/nginx   1         89b0e8f41524     2 minutes ago    150MB
# ubuntu             16.04     330ae480cb85     8 days ago       125MB
# docker/whalesay    latest    6b362a9f73eb     5 years ago      247MB
```

## 1.4 도커파일 작성

### 1.4.1 Dockerfile 기초

```python
# hello.py
import os
import sys

my_ver = os.environ["my_ver"]
arg = sys.argv[1]

print("hello %s, my version is %s!" % (arg, my_ver))
```

```Dockerfile
# Dockerfile
FROM ubuntu:20.04

RUN apt-get update \
    && apt-get install -y \
      curl \
      python-dev

WORKDIR /root
COPY hello.py .
ENV my_ver 1.0

CMD ["python", "hello.py", "guest"]
```

### 1.4.2 도커 빌드

```bash
# 현재 디렉토리에 위치한 Dockerfile을 이용하여 hello:1 이미지를 생성하라
docker build . -t hello:1
# Sending build context to Docker daemon   21.5kB
# Step 1/6 : FROM ubuntu:20.04
#  ---> 8e4ce0a6ce69
# Step 2/6 : RUN apt-get update && apt-get install -y curl
#  ---> Running in 2d62d9ed92f
# ...

docker run hello:1
# hello guest, my version is 1.0!

# 파라미터를 넘기게 되면 기존 `CMD`는 override 됩니다.
# echo
docker run hello:1 echo "hello world!"
# hello world!

# cat
docker run hello:1 cat hello.py
# import os
# import sys
# ...

# pwd
docker run hello:1 pwd
# /root
```

```bash
docker run -e my_ver=1.5 hello:1
# hello guest, my version is 1.5!
```

### 1.4.3 Dockerfile 심화

#### ARG

```Dockerfile
# Dockerfile
FROM ubuntu:20.04

RUN apt-get update \
    && apt-get install -y \
      curl \
      python-dev

ARG my_ver=1.0

WORKDIR /root
COPY hello.py .
ENV my_ver $my_ver

CMD ["python", "hello.py", "guest"]
```

```bash
docker build . -t hello:2 --build-arg my_ver=2.0

docker run hello:2
# hello guest, my version is 2.0!
```

```bash
docker run -e my_ver=2.5 hello:2
# hello guest, my version is 2.5!
```

#### ENTRYPOINT

```Dockerfile
# Dockerfile
FROM ubuntu:20.04

RUN apt-get update \
    && apt-get install -y \
      curl \
      python-dev

WORKDIR /root
COPY hello.py .
ENV my_ver 1.0

ENTRYPOINT ["python", "hello.py", "guest"]
```

```bash
docker build . -t hello:3

docker run hello:3
# hello guest, my version is 1.0!

# 실행명령을 전달해도 ENTRYPOINT 그대로 실행됩니다.
docker run hello:3 echo "hello"
# hello guest, my version is 1.0!
```

```Dockerfile
# Dockerfile
FROM ubuntu:20.04

RUN apt-get update \
    && apt-get install -y \
      curl \
      python-dev

WORKDIR /root
COPY hello.py .
ENV my_ver 1.0

# guest를 삭제합니다. hello.py가 새로운 파라미터를 받을 수 있게 만듭니다.
ENTRYPOINT ["python", "hello.py"]
```

```bash
docker build . -t hello:4

# new-guest 파라미터를 전달합니다.
docker run hello:4 new-guest
# hello new-guest, my version is 1.0!
```

## 1.5 도커 실행 고급

### 1.5.1 Network

```bash
docker run -p 5000:80 -d nginx
# rlasdf0234klcvmz904390zxhvksdf230zxc

# 5000번으로 localhost 호출을 합니다.
curl localhost:5000
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...

# 내부/공인IP로도 확인해 봅니다.
curl <내부 혹은 공인IP>:5000
# <!DOCTYPE html>
# <html>
# <head>
# <title>Welcome to nginx!</title>
# ...
```

### 1.5.2 Volume

```bash
# 현재 디렉토리를 컨테이너의 nginx 디렉토리와 연결합니다.
docker run -p 6000:80 -v $(pwd):/usr/share/nginx/html/ -d nginx

# 현재 디렉토리에 hello.txt 파일을 생성합니다.
echo hello! >> $(pwd)/hello.txt

# nginx 내부에서 해당 파일이 보이는지 확인합니다.
curl localhost:6000/hello.txt
# hello!
```

### 1.5.3 Entrypoint

```Dockerfile
# Dockerfile
FROM ubuntu:18.04

ENTRYPOINT ["echo"]
```

```bash
docker build . -t lets-echo

docker run lets-echo hello
# hello

# cat의 결과가 출력되는 것을 기대하나 cat '/etc/passwd' 라는 문자열이 출력됨
docker run lets-echo cat /etc/password
# cat /etc/password

# entrypoint를 cat 명령으로 override
docker run --entrypoint=cat lets-echo /etc/passwd
# root:x:0:0:root:/root:/bin/bash
# daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
# bin:x:2:2:bin:/bin:/usr/sbin/nologin
# ...
```

### 1.5.4 User

```Dockerfile
# Dockerfile
FROM ubuntu:18.04

# Ubuntu 유저 생성
RUN adduser --disabled-password --gecos "" ubuntu

# 컨테이너 실행 시 ubuntu 유저로 설정
USER ubuntu
```

```bash
# my-user 라는 이미지 생성
docker build . -t my-user

# ubuntu라는 유저로 컨테이너 실행
docker run -it my-user bash
ubuntu@b09ce82d4a77:/$

ubuntu@b09ce82d4a77:/$ apt update
# Reading package lists... Done
# E: List directory /var/lib/apt/lists/partial is missing.
# - Acquire (13: Permission denied)

ubuntu@b09ce82d4a77:/$ exit

# 강제로 root 유저 사용
docker run --user root -it my-user bash
root@0ac2522215e8:/$ apt update
# Get:1 http://security.ubuntu.com/ubuntu bionic-security InRelease
# Get:2 http://archive.ubuntu.com/ubuntu bionic InRelease [242 kB]
# ...

root@0ac2522215e8:/$ exit
```

### Clean up

```bash
docker rm $(docker ps -aq) -f
docker rmi $(docker images -q) -f
```
