FROM python:3.10
COPY requirements.txt /
RUN pip install -r /requirements.txt
ADD . /cel-worker
WORKDIR /cel-worker
ENTRYPOINT celery -A tasks.cel worker --loglevel=info