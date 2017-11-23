# -*- coding: utf-8 -*-
import config
import telebot
from answerer import *
import copy

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Якупов Тимур")


@bot.message_handler(content_types=["text"])
def respond(message):
    result = ""
    data = answer(message.text)
    for i in data:
        result += "Question: " + i[0] + "\nAnswer: " + i[1] + "Confidence: " + str(i[2]) + "\n"
        result += "-" * 15 + "\n"
    bot.send_message(message.chat.id, result)


if __name__ == '__main__':
    bot.polling(none_stop=True)



