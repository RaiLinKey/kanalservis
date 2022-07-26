import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_chat_ids():
    try:
        conn = psycopg2.connect(
            user='postgres',
            password='1234',
            host='127.0.0.1',
            port='5432',
            database='kanalservis'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        sql = "select * from telegram_users order by id"
        cursor.execute(sql)
        data = []
        for row in cursor:
            data += [(row[1], row[2])]
        return tuple(data)
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Соединение с PostgreSQL закрыто")


print(get_chat_ids())
