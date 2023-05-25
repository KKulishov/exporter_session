import time
import socket
from os import getenv, path
import mysql.connector
from prometheus_client import start_http_server, generate_latest
from prometheus_client.core import REGISTRY, CounterMetricFamily, GaugeMetricFamily, Gauge

EXPORTER_ENV = getenv("EXPORTER_ENV")
if EXPORTER_ENV == "PROD":
    host_db = getenv("MYSQL_HOST")
    password_db = getenv("MYSQL_PASSWORD")
    user_db = getenv("MYSQL_USER")
    db_name = getenv("MYSQL_DATABASE")
    port_db = '3306'
elif EXPORTER_ENV == "DEV":
    host_db = '172.16.10.97'
    password_db = 'pass'
    user_db = 'root'
    db_name = 'db_ds'
    port_db = '3307'
else:
    print('Переменная EXPORTER_ENV не задана или задано, но она несоотвествует значением PROD или DEV')

port_exporter = 8000

def db_session_check():
    time.sleep(2)
    records = [(0, 0)]
    query = "SELECT user_id, id as Session_id, TIMEDIFF(NOW(), updated_date) as diff, NOW(), updated_date FROM db_ds.sessions where status=\"estimating\" and created_date >= \"2021-10-01 00:00:00\" having  diff > \"1:0:0\";"
    dbconnect = mysql.connector.connect(
        host=host_db,
        port=port_db,
        user=user_db,
        password=password_db,
        db=db_name
    )
    with dbconnect.cursor() as cursor:
        cursor.execute(R"""
            SELECT user_id, id as Session_id, TIMEDIFF(NOW(), updated_date) as diff, NOW(), updated_date
            FROM db_ds.sessions where 
            status="estimating" and created_date >= "2021-10-01 00:00:00" and id not in (1164,1165,1166,1167,1168,1169,1170,1247,1248, 1249,1250)
            having diff > "01:00:00";
            """)
        try:
            records = cursor.fetchall()
        except:
            user_id = 0
            session_id = 0
        dbconnect.commit()
    return records


class CustomServiceExporter:
    def collect(self):
        host_name = socket.gethostname()
        db_session_result = db_session_check()

        metrics_list_count_dir_db = GaugeMetricFamily(
            "freeze_session",
            "Прочтение, зависание расчета",
            labels=["session_id", "host_db"]
        )

        #print(db_session_result)

        for record in db_session_result:
            user_id = str(record[0])
            session_id = str(record[1])
            # в label добавить значение namespace и может имя БД
            metrics_list_count_dir_db.add_metric([session_id, host_db], user_id)
        yield metrics_list_count_dir_db

REGISTRY.register(CustomServiceExporter())

if __name__ == '__main__':
    start_http_server(port_exporter)
    while True:
        # частота посылаемых запросов
        time.sleep(20)
        generate_latest()
