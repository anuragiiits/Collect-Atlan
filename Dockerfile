FROM python:3.6.7

ENV PYTHONUNBUFFERED 1
RUN mkdir /Atlan
WORKDIR /Atlan
ADD . /Atlan/
RUN pip install -r requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "Collect.wsgi:application"]