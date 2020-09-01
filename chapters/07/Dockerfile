# Dockerfile
FROM python:3.6.8-stretch

RUN pip install tensorflow==1.5 keras==2.0.8 h5py==2.7.1

COPY train.py .

ENTRYPOINT ["python", "train.py"]