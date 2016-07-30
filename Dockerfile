FROM python:3.5.1

ENV DJANGO_CONFIG=production

ADD requirements.in /code/
WORKDIR /code
RUN pip install pip-tools
RUN pip-compile requirements.in
RUN pip install -r requirements.txt
