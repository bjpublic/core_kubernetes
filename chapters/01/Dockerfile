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