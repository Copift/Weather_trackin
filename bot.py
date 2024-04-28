import random
import re
import mysql.connector
import telebot
from telebot import types
from telebot.types import Message

token = '6377287085:AAElOAKNyIXqlX9ZA0xAvuK68CWcskm-umk'  # ЭТО ТОКЕН КОТОРЫЙ НАДО СКОПИРОВАТЬ ЧТОБЫ ПОЛУЧИТЬ ДОСТУП К ТЕЛЕГЕ БОТУ ЕГО НЕЛЬЗЯ ПОКАЗЫВАТЬ!!!
bot = telebot.TeleBot(token)
users={}
cnx=mysql.connector.connect(host='10.8.0.1',user='adm',password='1qaz@WSX12',database='weather_tracking_test')
cursor=cnx.cursor()
def createMainMenu():
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Мои станции")
    item2=types.KeyboardButton("Удалить станцию")
    item3=types.KeyboardButton("Добавить станцию")
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    print(message)
    mesg=bot.send_message(message.chat.id,f'Добрый день, укаажите ваше имя для регистрации системы уведомлений',parse_mode='HTML')
    bot.register_next_step_handler(mesg, registration)
def registration(message: Message):
    name=message.text
    try:
        print(int(message.from_user.id))
        cursor.execute(f"INSERT INTO Users_info (user_id,user_name) VALUES ({int(message.from_user.id)},'{name}')")
        #cnx.commit()
    except mysql.connector.errors.IntegrityError as err:
       bot.send_message(message.chat.id,f'Вы уже зарегистрированы в системе уведомлений',parse_mode='HTML')
    mesg=bot.send_message(message.chat.id, f'{name} введите номер вашего устройства (id  на коробке или на главном экране настроек)',
                     parse_mode='HTML')
    bot.register_next_step_handler(mesg, add_new)
def add_new(message: Message):
    id=message.text.strip()
    if re.match("^\d{0,7}$", id):
        id=int(id)
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        mesg = bot.send_message(message.chat.id, f'нажмите на  кнопку для отправки координат',
                                parse_mode='HTML', reply_markup=keyboard)
        # Клавиатура с кнопкой запроса локации


        bot.register_next_step_handler(mesg, location,id )
    else:
        mesg=bot.send_message(message.chat.id,f'id не соотвествует формату - попробуйте еще раз (7 цифр)',parse_mode='HTML')
        bot.register_next_step_handler(mesg, add_new,)
@bot.message_handler(content_types=['location'])
def location (message,id):
    if message.location is not None:
        print(message.location)
        cursor.execute(f"INSERT INTO  Trackers_info \
        (tracker_id, tracker_owner_id, tracker_coordinates) \
        VALUES({id},{int(message.from_user.id)} , '{message.location.latitude};{message.location.longitude}');")
        cnx.commit()
        bot.send_message(message.chat.id, f'устройство  успешно добавлено' ,reply_markup=createMainMenu())
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(message.chat.id, "ошибка - попробуйте еще раз", reply_markup=keyboard)
@bot.message_handler(content_types='text')
def message_reply(message:Message):
    if message.text == "Мои станции":
        cursor.execute(f"SELECT tracker_id \
FROM  Trackers_info where tracker_owner_id = {message.from_user.id};")

        stations=list(cursor.fetchall())
        answer='ваши станции: \n'
        for station in stations:
            answer+=f'->{station[0]} \n'
        bot.send_message(message.chat.id,answer,parse_mode='HTML', reply_markup=createMainMenu())
    if message.text == "Удалить станцию":
        mesg=bot.send_message(message.chat.id,'введите id станции для удаления',reply_markup=None)
        bot.register_next_step_handler(mesg, delete, )
    if message.text == "Добавить станцию":
        mesg = bot.send_message(message.chat.id,
                                f' введите номер вашего устройства (id  на коробке или на главном экране настроек)',
                                parse_mode='HTML',reply_markup=None)
        bot.register_next_step_handler(mesg, add_new)
def delete(message:Message):
    id = message.text.strip()
    if re.match("^\d{0,7}$", id):
        id = int(id)
        cursor.execute(f"DELETE FROM Trackers_info where tracker_id = {id};")
        cnx.commit()
        bot.send_message(message.chat.id, f'устройство  успешно удалено',reply_markup=createMainMenu())

    else:
        mesg = bot.send_message(message.chat.id, f'id не соотвествует формату - попробуйте еще раз (7 цифр)',
                                parse_mode='HTML',)
        bot.register_next_step_handler(mesg,delete, )
bot.infinity_polling()