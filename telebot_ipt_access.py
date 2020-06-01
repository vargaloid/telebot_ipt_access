#!/usr/bin/env python3

import config
import telebot
import datetime
from subprocess import call
from ipaddress import ip_address
from collections import defaultdict

bot = telebot.TeleBot(config.Token)

# Состояние пользователя (шаг)
START, IP = range(2)

USER_STATE = defaultdict(lambda: START)
server_ip = '192.168.122.240:3389'


# ====== Функции состояния пользователя ====== #
def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


# ====== Обработка команды START ====== #
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.chat.id
    user_username = message.chat.username
    user_first_name = message.chat.first_name
    user_last_name = message.chat.last_name
    now = datetime.datetime.now()
    now_time = str(now.strftime("%d-%m-%Y %H:%M"))
    f = open("users.txt", "a")
    f.write(str(now_time) + ': ' + str(user_id) + ' ' + str(user_username) + ' ' + str(user_first_name) + ' ' + str(user_last_name) + '\n')
    f.close()


# ====== Обработка команды ADD ====== #
@bot.message_handler(commands=['add'])
def start_handler(message):
    user_id = message.chat.id
    if str(user_id) in config.admin_id:
        bot.send_message(user_id, 'Введите ip-адрес в формате 192.168.12.34')
        update_state(message, IP)
    else:
        True


# ====== Обработчик IP ====== #
@bot.message_handler(func=lambda message: get_state(message) == IP)
def handle_ip(message):
    user_id = message.chat.id
    user_ip = message.text
    try:
        ip = ip_address(user_ip.split()[0])
        try:
            # ipset
            call(["ipset", "-A", "truerdp", str(ip)])
            call(["ipset", "save", "truerdp"])
            call(["ipset", "-S", ">", "/etc/ipset-save"])
            bot.send_message(user_id, "IP-адрес " + str(ip) + " добавлен")
            update_state(message, START)
        except:
            bot.send_message(user_id, "Ошибка добавления")
    except ValueError:
        bot.send_message(user_id, 'Неправильный формат ip-адреса')
    except IndexError:
        bot.send_message(user_id, 'Bad input string')


if __name__ == '__main__':
    bot.polling(none_stop=True)
