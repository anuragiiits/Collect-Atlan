FROM python:3.6.7

ENV PYTHONUNBUFFERED 1
RUN mkdir /Atlan
WORKDIR /Atlan
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./ ./
ENV DEBUG=1
ENV ALLOWED_HOSTS=*
ENV SECRET_KEY=somesecretkey
RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations --noinput
RUN python manage.py migrate --noinput
CMD ["./start.sh"]
