FROM python:3.9-slim

RUN mkdir -p /app
RUN useradd app
RUN chown -R app:app /app 
WORKDIR /app

EXPOSE 8000

RUN pip install mysql-connector-python prometheus-client

COPY main.py /app/
COPY entrypoint.sh /app/

ENTRYPOINT ["/entrypoint.sh"]

