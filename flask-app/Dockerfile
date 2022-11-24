FROM python:3.10
COPY requirements.txt /
RUN pip install -r /requirements.txt
ADD . /flask-app
WORKDIR /flask-app
ENV FLASK_ENV=development
CMD flask run --host=0.0.0.0