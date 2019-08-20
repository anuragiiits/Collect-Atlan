FROM python:3.6.7

ENV PYTHONUNBUFFERED 1
RUN mkdir /Atlan
WORKDIR /Atlan
ADD . /Atlan/
RUN pip install -r requirements.txt

EXPOSE 8000