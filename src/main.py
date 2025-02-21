import telebot
import webbrowser
from array import *
from telebot import types

bot = telebot.TeleBot('7760507421:AAFQ2xUSEf8T78A6MrB7aHaexz-2BaOcDGg')

'''@bot.message_handler(commands=['site'])
def main(message):
    webbrowser.open('https://mdl.sch239.net/course/view.php?id=368')'''

categories = {
    'Категория 1': ['task1', 'task2'],
    'Категория 2': ['task3', 'task4']
}


def toString(slovar):
    result = ''
    for key in slovar:
        result += key + '\n'
        for item in slovar[key]:
            result += '- ' + item + '\n'
        result += '\n'
    return result


@bot.message_handler(commands=['start'])
def mainProgress(message1):
    markup = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton('Добавить задачу')
    btn2 = types.KeyboardButton('Добавить категорию')
    markup.row(btn1, btn2)

    bot.send_message(message1.chat.id, toString(categories), reply_markup=markup)
    bot.register_next_step_handler(message1, funcProgress)


def funcProgress(message2):
    if message2.text == 'Добавить задачу':
        markup = types.InlineKeyboardMarkup()

        btns = []
        for key in categories:
            btns.append(types.InlineKeyboardButton(key, callback_data=key))

        for btn in btns:
            markup.row(btn)
        bot.reply_to(message2, 'Выберите категорию:', reply_markup=markup)

        bot.register_next_step_handler(message2, mainProgress)
    elif message2.text == 'Добавить категорию':
        bot.send_message(message2.chat.id, 'Введите название категории:')


# обработка callback_data
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    bot.send_message(callback.message.chat.id, 'Введите задачу:')
    bot.register_next_step_handler(callback.message, appendTask, callback.data)

    #bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)  # удаляет предпоследнее сообщение
    #elif callback.data == '2':
    #   bot.edit_message_text('Edited text', callback.message.chat.id, callback.message.message_id)


def appendTask(message, key):
    categories[key].append(message.text)
    #bot.send_message(message.chat.id, toString(categories))



'''@bot.message_handler(commands=['x'])
def start(message):
    markup = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton('Перейти на сайт')
    markup.row(btn1)
    btn2 = types.KeyboardButton('Удалить предпоследнее сообщение')
    btn3 = types.KeyboardButton('Изменить текст')
    markup.row(btn2, btn3)

    bot.send_message(message.chat.id, 'Buttons created', reply_markup=markup)
    bot.register_next_step_handler(message, func)'''

'''def func(message):
    if message.text == 'Перейти на сайт':
        bot.send_message(message.chat.id, 'Website opened')
        webbrowser.open('https://mdl.sch239.net/course/view.php?id=368')
    elif message.text == 'Удалить предпоследнее сообщение':
        bot.send_message(message.chat.id, 'Message deleted')
    #bot.register_next_step_handler(message, func)'''

'''@bot.message_handler(content_types=['photo'])
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Перейти на сайт', url='https://mdl.sch239.net/course/view.php?id=368'))

    btn2 = types.InlineKeyboardButton('Удалить фото', callback_data='delete')
    btn3 = types.InlineKeyboardButton('Изменить текст', callback_data='edit')
    markup.row(btn2, btn3)
    bot.reply_to(message, 'Photo', reply_markup=markup)'''

'''@bot.message_handler(commands=['hello', 'main'])
def main(message):
    bot.send_message(message.chat.id, f'hello {message.from_user.first_name} {message.from_user.last_name}')

@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, '<b>here</b> <em>you</em> <u>go</u>', parse_mode='html')

@bot.message_handler()
def info(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
    elif message.text.lower() == 'id':
        bot.reply_to(message, f'ID: {message.from_user.id}')'''

bot.polling(none_stop=True)
