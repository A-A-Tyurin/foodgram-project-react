FROM python:3.8.5
WORKDIR /app_code
COPY /foodgram/requirements.txt .
RUN pip3 install -r requirements.txt
COPY /foodgram .
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000