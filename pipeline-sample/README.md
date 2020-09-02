# pipeline-sample

## CI 파이프라인

Jenkins CI 파이프라인을 위한 샘플코드입니다.

다음과 같은 파일들이 있습니다.

- `app.py`: CI/CD를 통해 쿠버네티스 클러스터로 배포하려는 어플리케이션 소스코드입니다.
- `Dockerfile`: 소스코드를 실행가능한 파일(도커 이미지)로 변환하는 도커파일입니다.
- `test.py`: CI 파이프라인에서 테스트를 담당하는 스크립트입니다.
- `test.sh`: `docker run --entrypoint=/test` 명령을 이용하여 테스트 수행 시, 실제 실행되는 스크립트입니다.

CI 파이프라인은 다음과 같은 흐름을 가집니다.

```bash
# 소스코드 checkout
git clone $PROJECT_NAME
git checkout $BRANCH

# 빌드 Artifact 생성
docker build . -t $PROJECT_NAME

# 빌드 결과물 테스트
docker run --entrypoint=/test $PROJECT_NAME

# 빌드 결과물 저장
docker push docker.io/$PROJECT_NAME
```

## 도커 안에 도커

도커 안에서 호스트 서버의 도커 데몬을 접근하기 위해서는 다음과 같이 실행합니다.

```bash
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock docker
```

호스트 도커 데몬과 통신할 수 있는 소켓파일을 볼륨으로 넘겨줌으로써 컨테이너 안에서 호스트 도커 데몬을 호출할 수 있게 실행합니다.

[Docker in Docker 읽을거리](https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/)
