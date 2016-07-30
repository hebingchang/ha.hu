FROM python:3.5.1

ADD requirements.in ./requirements.in
RUN pip install pip-tools
RUN pip-compile requirements.in
RUN pip install -r requirements.txt
