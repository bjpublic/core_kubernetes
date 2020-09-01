<!--
  Title: 핵심만 콕 쿠버네티스
  Description: 쿠버네티스의 소문에 대해 얘기는 들어봤지만 내용이 방대하고 설치하기가 어려워 선듯 시작하기 힘들었던 분들을 위한 책입니다. 이 책은 쿠버네티스 기본 개념부터 쿠버네티스 설치 방법까지 쿠버네티스를 시작하기 위해 필요한 핵심적인 내용들을 담고 있어 처음 쿠버네티스를 접하시는 분들이 빠르게 쿠버네티스를 이해하기 위해 만들어졌습니다.
  Author: 커피고래
-->

# 핵심만 콕 쿠버네티스

저서 "핵심만 콕 쿠버네티스"에 대한 예제코드 및 참고자료를 제공합니다.

## 예제코드

다음과 같이 Chapter별 예제코드를 참고할 수 있습니다.

- [Chapter 01: 도커기초](chapters/01)
- [Chapter 02: 쿠버네티스 소개](chapters/02)
- [Chapter 03: 쿠버네티스 설치](chapters/03)
- [Chapter 04: 쿠버네티스 첫 만남](chapters/04)
- [Chapter 05: Pod 살펴보기](chapters/05)
- [Chapter 06: 쿠버네티스 네트워킹](chapters/06)
- [Chapter 07: 쿠버네티스 컨트롤러](chapters/07)
- [Chapter 08: helm 패키지 매니저](chapters/08)
- [Chapter 09: Ingress 리소스](chapters/09)
- [Chapter 10: 스토리지](chapters/10)
- [Chapter 11: 고급 스케줄링](chapters/11)
- [Chapter 12: 클러스터 관리](chapters/12)
- [Chapter 13: 접근 제어](chapters/13)
- [Chapter 14: 로깅과 모니터링](chapters/14)
- [Chapter 15: CI/CD](chapters/15)
- [Chapter 16: 사용자 정의 리소스](chapters/16)
- [Chapter 17: 워크플로우 관리](chapters/17)

---

## 참고자료

### VirtualBox를 이용한 k3s 클러스터 구축 방법 소개

Chapter 3 `쿠버네티스 설치`에 대한 참고자료입니다. 내 로컬 PC(윈도우)에서 클러스터를 구축하기 위해 VirtualBox를 이용하여 k3s 클러스터를 구축하는 방법에 대해서 소개합니다.

- [VirtualBox를 이용한 k3s 클러스터 구축](https://coffeewhale.com/kubernetes/cluster/virtualbox/2020/08/31/k8s-virtualbox)

### 클라우드 서비스별 클러스터 구축 방법 소개

Chapter 11 `고급 스케줄링`에서 Node 레벨 고가용성 확보를 위한 Cluster Auto Scaler 예제를 따라하기 위한 클라우드 서비스별 클러스터 구축 방법을 설명드립니다.

- [AWS EKS 클러스터 구축](https://coffeewhale.com/kubernetes/cluster/eks/2020/09/03/k8s-eks/)
- [GCP GKE 클러스터 구축](https://coffeewhale.com/kubernetes/cluster/gke/2020/09/04/k8s-gke/)

### CI Pipeline 샘플코드

Chapter 15 `CI/CD`에서 Jenkins CI pipeline으로 활용하는 샘플코드입니다.

- [pipeline-sample/](pipeline-sample/) 디렉토리 참조 바랍니다.


### GitOps 단일 진실의 원천 배포 디렉토리

Chapter 15 `CI/CD`에서 FluxCD, ArgoCD에서 단일 진실의 원천으로 사용하는 샘플코드입니다.

- [gitops/](gitops/) 디렉토리 참조 바랍니다.

---

## 오탈자 제보 및 문의 사항

다음 2가지 방법을 이용하여 연락주시기 바랍니다.

- 깃허브 리파지토리 [issue 생성](https://github.com/bjpublic/core_kubernetes/issues/new)
- `hongkunyoo (at) gmail.com` (저자, 유홍근)으로 메일 전송
