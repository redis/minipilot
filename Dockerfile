FROM docker.io/python:3.9
WORKDIR /app
COPY src /app/src/
COPY requirements.txt wsgi.py /app

RUN pip install --no-cache-dir -r requirements.txt

ENV GUNICORN_CMD_ARGS="--workers 1 --bind 0.0.0.0:8000 --timeout 600 --log-level debug --capture-output --error-logfile ./gunicorn.log"
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD [ "gunicorn", "wsgi:create_app()" ]
