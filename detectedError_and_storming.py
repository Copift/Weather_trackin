import mysql.connector
import datetime
import telebot
from telebot import types
from telebot.types import Message
token = '6377287085:AAElOAKNyIXqlX9ZA0xAvuK68CWcskm-umk'  # ЭТО ТОКЕН КОТОРЫЙ НАДО СКОПИРОВАТЬ ЧТОБЫ ПОЛУЧИТЬ ДОСТУП К ТЕЛЕГЕ БОТУ ЕГО НЕЛЬЗЯ ПОКАЗЫВАТЬ!!!
bot = telebot.TeleBot(token)
config = {
            "host": '10.8.0.1',
            "user": 'adm',
            "port": 3306,
            "password": '1qaz@WSX12',
            "database": 'weather_tracking_test',
        }

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
cursor.execute("SELECT      t.tracker_owner_id, w.predicted_measurement_date,  w.tracker_id, w.predicted_pressure, w.is_storm, w.predicted_temp  \
FROM weather_tracking_test.Predicted_weather w join Trackers_info t on w.tracker_id=t.tracker_id where is_storm is true  ; ")
for storm in cursor.fetchall():
    try:
        bot.send_message(storm[0],f"Ожидается шторм на {storm[1]} по данным станции {storm[2]}")
    except Exception as err:
        pass
already_check={}
tracker_owner={}
cursor.execute(" SELECT t.tracker_owner_id, w.real_measurement_date, w.tracker_id, w.real_pressure, w.real_temperature \
FROM weather_tracking_test.Weather_data w join Trackers_info t on w.tracker_id=t.tracker_id GROUP BY tracker_id;")
for tracker in cursor.fetchall():
        already_check.update({tracker[2]:tracker[1]})
        tracker_owner.update({tracker[2]: tracker[0]})
for tracker in already_check.keys():
    if already_check[tracker]<datetime.datetime.now() - datetime.timedelta(days=4):
        try:
            bot.send_message(storm[0], f"Ваша станция не отвечает {tracker[2]}")
        except Exception as err:
            pass

