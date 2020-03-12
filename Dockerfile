
FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
ENV UWSGI_INI /app/uwsgi.ini

COPY app.conf /etc/nginx/conf.d/
COPY requirements.txt /app
WORKDIR /app
COPY ./app /app

RUN apk --update add build-base libffi-dev openssl-dev
RUN pip install -r requirements.txt
RUN apk del build-base libffi-dev openssl-dev

#ON AZURE SET: WEBSITES_PORT with a value that matches the port here
EXPOSE 5000


#RUN apk --update add build-base libffi-dev openssl-dev python-dev py-pip
#RUN pip install -r requirements.txt
#RUN apk del build-base libffi-dev openssl-dev python-dev py-pip

