FROM python:3.10 
# Or any preferred Python version.


WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app
EXPOSE 8000
CMD python manage.py migrate && gunicorn -c conf/gunicorn_config.py  chestgold.wsgi