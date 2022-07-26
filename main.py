import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import xml.etree.cElementTree as Et
import wget
from datetime import datetime, timedelta
import os
from math import ceil
from time import sleep

CREDENTIALS_FILES = 'credentials.json'
spreadsheet_id = '1gv6K3S_gltFpsH4xsYGYKjYGEx1hj3eSFWX5e8xPrK4'
user = 'postgres',
password = '1234',
host = '127.0.0.1',
port = '5432',
database = 'kanalservis'


# функция получения значений из Google Sheets
def get_values() -> tuple:
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILES,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
    )
    try:
        httpAuth = credentials.authorize(httplib2.Http())
        service = build('sheets', 'v4', http=httpAuth)

        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='A1:D1250000',
            majorDimension='ROWS'
        ).execute()['values'][1:]
        for value in values:
            if len(value) < 4:
                values.remove(value)
        return tuple(values)
    except HttpError as error:
        print(f"Ошибка при обращении к Google API: {error}")
        return error,


# функция получения текущего курса доллара к рублю от ЦБ
def usd_curs() -> int:
    today = datetime.today().date()
    try:
        tree = Et.parse('tmp/XML_daily.asp')
    except FileNotFoundError:
        wget.download(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={today.strftime("%d/%m/%Y")}', 'tmp/')
        tree = Et.parse('tmp/XML_daily.asp')

    valute_date = datetime.strptime(tree.getroot().attrib['Date'], '%d.%m.%Y').date()
    if valute_date <= today <= valute_date + timedelta(days=1):
        return ceil(float(tuple(tree.find('Valute[@ID="R01235"]'))[4].text.replace(',', '.')))
    else:
        os.remove('tmp/XML_daily.asp')
        wget.download(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={today.strftime("%d/%m/%Y")}', 'tmp/')
        tree = Et.parse('tmp/XML_daily.asp')
        return ceil(float(tuple(tree.find('Valute[@ID="R01235"]'))[4].text.replace(',', '.')))


# функция занесения данных в БД
def insert_data_to_db(values: tuple):
    try:
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        db_values = ''
        cursor = conn.cursor()
        for value in values:
            try:
                date = datetime.strptime(value[3], '%d.%m.%Y').date()
                if str(value[0]).isdigit() and str(value[1]).isdigit() and str(value[2]).isdigit():
                    if db_values:
                        db_values += f", ({value[0]}, {value[1]}, {value[2]}, '{date}', {int(value[2]) * usd_curs()})"
                    else:
                        db_values += f"({value[0]}, {value[1]}, {value[2]}, '{date}', {int(value[2]) * usd_curs()})"
                else:
                    continue
            except (Exception, Error) as error:
                print("Ошибка валидации данных", error)

        sql = f'insert into ksfront_sheetdata values {db_values}'
        print(sql)
        cursor.execute(sql)
        print("Добавление данных в PostgreSQL прошло успешно")

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Соединение с PostgreSQL закрыто")


# функция получения данных из БД
def get_data_from_db() -> tuple:
    try:
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        sql = "select * from ksfront_sheetdata order by id"
        cursor.execute(sql)
        data = []
        for row in cursor:
            data += (row,)
        return tuple(data)

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Соединение с PostgreSQL закрыто")


# функция удаления из БД
def delete_from_db(values: tuple):
    try:
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        delete_data = ''
        for val in values:
            if str(val[1]).isdigit():
                if delete_data:
                    delete_data += f' or order_no = {val[1]}'
                else:
                    delete_data += f'order_no = {val[1]}'
            else:
                print(f'Параметр {val[1]} не прошёл валидацию')
        if delete_data:
            sql = f"delete from ksfront_sheetdata where {delete_data}"
            cursor.execute(sql)
            print("Удаление из PostgreSQL прошло успешно")
        else:
            print("Удаление из PostgreSQL не было произведено")

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Соединение с PostgreSQL закрыто")


# функция обнволения данных в БД
def update_data_in_db(values: list):
    try:
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        date = datetime.strptime(values[3], '%d.%m.%Y').date()
        if str(values[0]).isdigit() and str(values[1]).isdigit() and str(values[2]).isdigit():
            sql = f"update ksfront_sheetdata " \
                  f"set usd_price = {values[2]}, delivery_time = '{date}', rub_price = {int(values[2]) * usd_curs()} " \
                  f"where order_no = {values[1]}"
            cursor.execute(sql)
            print("Обновление данных в PostgreSQL прошло успешно")
        else:
            print("Данные не прошли валидацию и не были обновлены")

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Соединение с PostgreSQL закрыто")


# функция анализа сравнения и обработки разницы между Google Sheets и БД
def analyze(values: tuple, db_data: tuple):
    values_orders = tuple((int(x[1]) for x in values))
    data_orders = tuple((int(x[1]) for x in db_data))
    val_diff = tuple(set(values_orders) - set(data_orders))
    data_diff = tuple(set(data_orders) - set(values_orders))

    if val_diff:
        new_values = []
        for val in val_diff:
            new_values += [values[values_orders.index(val)]]
        print(new_values)
        insert_data_to_db(tuple(new_values))
        db_data = get_data_from_db()
    if data_diff:
        old_data = []
        for data in data_diff:
            old_data += [db_data[data_orders.index(data)]]
        print(old_data)
        delete_from_db(tuple(old_data))
        db_data = get_data_from_db()
    for i in range(len(values)):
        try:
            if int(values[i][2]) != db_data[i][2] or datetime.strptime(values[i][3], '%d.%m.%Y').date() != db_data[i][
                3]:
                update_data_in_db(values[i])
                print('UPDATED')
        except ValueError:
            print(f'Данные {values[i]} не прошли валидацию')
        except IndexError:
            print(f'Данные {values[i]} ещё не добавлены в БД')


if __name__ == '__main__':
    try:
        while True:
            vals = get_values()
            data_from_db = get_data_from_db()
            analyze(vals, data_from_db)
            sleep(5)
    except KeyboardInterrupt:
        pass
