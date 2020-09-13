FROM python:3.7

RUN pip install flask pytest

WORKDIR /work
COPY test.sh /test
COPY test.py test.py
COPY app.py app.py

RUN chmod +x /test

CMD ["python", "app.py"]
