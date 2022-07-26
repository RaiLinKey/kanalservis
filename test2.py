from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters, InlineQueryHandler, JobQueue
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import time, datetime


TOKEN = '815843939:AAHUshmMbt2WVsuqypXbcJx1O1ATZqVFKTI'
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
notis_time = time(5, 21, 00, 000000, tzinfo=None)


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


def get_sent_notis(_chat_id):
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
        sql = "select t1.chat_id, t3.order_no from telegram_users as t1 " \
              "join sent_notis as t2 on t1.id=t2.user_id " \
              "join ksfront_sheetdata as t3 on t3.id=t2.order_id " \
              f"where t1.chat_id = '{_chat_id}'"
        cursor.execute(sql)
        data = []
        for row in cursor:
            data += (row[1],)
        return tuple(data)

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Соединение с PostgreSQL закрыто")


def new_sent_notis(_chat_id, orders):
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
        for order in orders:
            sql = f"call insert_sent_notis ('{_chat_id}', {order})"
            cursor.execute(sql)

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Соединение с PostgreSQL закрыто")


def get_data_from_db() -> tuple:
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


def new_chat_id(_chat_id: str):
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
        sql = f"insert into telegram_users (chat_id, status) values ({_chat_id}, True)"
        cursor.execute(sql)

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Соединение с PostgreSQL закрыто")


# функция обработки команды '/start'
def start(update, context):
    chat_id = update.effective_chat.id
    chat_ids = tuple(x[0] for x in get_chat_ids())
    print(chat_ids)
    if str(chat_id) not in chat_ids:
        new_chat_id(chat_id)
    text = "Здравствуйте!\nДанный бот будет присылать вам уведомление при обнаружении нарушения срока поставки.\n" \
           "Рассылка происходит в 10:00 по МСК\n\n" \
           "Чтобы отписаться от уведомлений, напишите команду /unsub\n" \
           "Для возобновления получения сообщений, напишите команду /sub"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


def notification(_chat_id, context):
    data = list(get_data_from_db())
    today = datetime.today().date()
    data_orders = []
    for d in data:
        if d[3] < today:
            data_orders += [d[1]]
    data_orders = tuple(data_orders)
    sent_notis_orders = get_sent_notis(_chat_id)
    not_sent = []
    for order in data_orders:
        if order not in sent_notis_orders:
            not_sent += [order]
    if not_sent:
        not_sent_str = '\n'.join(str(x) for x in not_sent)
        text = f"ВНИМАНИЕ! Нарушен срок поставки по следующим заказам:\n{not_sent_str}"
        context.bot.send_message(chat_id=_chat_id,
                                 text=text)
        new_sent_notis(_chat_id, not_sent)


def send_notis(context):
    for chat_id_data in get_chat_ids():
        if chat_id_data[1]:
            notification(int(chat_id_data[0]), context)


def unsub(update, context):
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
        sql = f"update telegram_users set status = false where chat_id = '{update.effective_chat.id}'"
        cursor.execute(sql)

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Соединение с PostgreSQL закрыто")

    text = 'Вы отписались от уведомлений!'
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


def sub(update, context):
    chat_id = update.effective_chat.id
    chat_ids = tuple(x[0] for x in get_chat_ids())
    if str(chat_id) not in chat_ids:
        new_chat_id(str(chat_id))
    else:
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

            sql = f"update telegram_users set status = true where chat_id = '{chat_id}'"
            cursor.execute(sql)

        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)

        finally:
            if conn:
                cursor.close()
                conn.close()
                print("Соединение с PostgreSQL закрыто")

    text = 'Вы подписались на уведомления!'
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


# функция обработки не распознных команд
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Простите, я нне знаю такой команды")


# обработчик команды '/start'
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# обработчик команды отписки от уведомлений
sub_handler = CommandHandler('sub', sub)
dispatcher.add_handler(sub_handler)

# обработчик команды подписки на уведомления
unsub_handler = CommandHandler('unsub', unsub)
dispatcher.add_handler(unsub_handler)

# обработчик не распознных команд
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

# ежедневное отправление уведомлений
jq = updater.job_queue
# job_minute = jq.run_repeating(send_notis, interval=60, first=5)
job_daily = jq.run_daily(send_notis, time=notis_time)

# запуск прослушивания сообщений
updater.start_polling()

# обработчик нажатия Ctrl+C
updater.idle()
