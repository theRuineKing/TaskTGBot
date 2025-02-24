import telebot
import webbrowser
from array import *
from telebot import types
from telebot.types import InlineKeyboardMarkup

botKey = '7760507421:AAFQ2xUSEf8T78A6MrB7aHaexz-2BaOcDGg'
bot = telebot.TeleBot(botKey)

heading = ''


categories = {
    'Категория 1': ['task1', 'task2'],
    'Категория 2': ['task3', 'task4']
}


def toString(slovar):
    result = ''
    if heading != '':
        result += heading + '\n\n'
    for key in slovar:
        result += key + '\n'
        for item in slovar[key]:
            result += '- ' + item + '\n'
        result += '\n'
    return result

@bot.message_handler(commands=['addtask', 'renametask', 'deletetask'])
def operateWithTask(message):
    markup = types.InlineKeyboardMarkup()

    btns = []
    if message.text == '/addtask':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='1'+key))
    elif message.text == '/renametask':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='2'+key))
    else:
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='4'+key))

    for btn in btns:
        markup.row(btn)
    bot.reply_to(message, 'Выберите категорию:', reply_markup=markup)

@bot.message_handler(commands=['addcategory'])
def addCategory(message):
    bot.send_message(message.chat.id, 'Введите название категории:')
    bot.register_next_step_handler(message, appendCategory)

@bot.message_handler(commands=['addheading'])
def addHeading(message):
    bot.send_message(message.chat.id, 'Введите название:')
    bot.register_next_step_handler(message, changeHeading)

'''@bot.message_handler(commands=['start'])
def mainProgress(message1):
    markup = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton('Добавить задачу')
    btn2 = types.KeyboardButton('Добавить категорию')
    markup.row(btn1, btn2)

    bot.send_message(message1.chat.id, toString(categories), reply_markup=markup)
    bot.register_next_step_handler(message1, funcProgress)

def funcProgress(message):
    if message.text == 'Добавить задачу':
        markup = types.InlineKeyboardMarkup()

        btns = []
        for key in categories:
            btns.append(types.InlineKeyboardButton(key, callback_data=key))

        for btn in btns:
            markup.row(btn)
        bot.reply_to(message, 'Выберите категорию:', reply_markup=markup)

    elif message.text == 'Добавить категорию':
        bot.send_message(message.chat.id, 'Введите название категории:')
        bot.register_next_step_handler(message, appendCategory)'''


# обработка callback_data
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    key = callback.data[1:]
    if callback.data[0] == '1':
        bot.send_message(callback.message.chat.id, 'Введите задачу:')
        bot.register_next_step_handler(callback.message, appendTask, key)

    elif callback.data[0] == '2' or callback.data[0] == '4':
        markup = types.InlineKeyboardMarkup()
        btns = []
        if callback.data[0] == '2':
            for i in range(len(categories[key])):
                btns.append(types.InlineKeyboardButton(categories[key][i], callback_data='3' + str(i) + '|' + key))
            for btn in btns:
                markup.row(btn)
            bot.reply_to(callback.message, 'Выберите задачу, которую хотите переименовать:', reply_markup=markup)
        else:
            for i in range(len(categories[key])):
                btns.append(types.InlineKeyboardButton(categories[key][i], callback_data='5' + str(i) + '|' + key))
            for btn in btns:
                markup.row(btn)
            bot.reply_to(callback.message, 'Выберите задачу, которую хотите удалить:', reply_markup=markup)

    elif callback.data[0] == '3':
        bot.send_message(callback.message.chat.id, 'Введите новое название задачи:')
        bot.register_next_step_handler(callback.message, renameTask,
                                       callback.data[callback.data.index('|')+1:],
                                       int(callback.data[1:callback.data.index('|')]))
    elif callback.data[0] == '5':
        bot.register_next_step_handler(callback.message, deleteTask,
                                       callback.data[callback.data.index('|')+1:],
                                       int(callback.data[1:callback.data.index('|')]))
    #bot.delete_message(callback.message.chat.id, callback.message.message_id - 1) удаляет предпоследнее сообщение
    #elif callback.data == '2':
    #bot.edit_message_text('Edited text', callback.message.chat.id, callback.message.message_id)

def appendTask(message, key):
    categories[key].append(message.text)
    bot.send_message(message.chat.id, toString(categories))

def renameTask(message, key, i):
    categories[key][i] = message.text
    bot.send_message(message.chat.id, toString(categories))

def deleteTask(message, key, i):
    categories[key].pop(i)
    bot.send_message(message.chat.id, toString(categories))

def appendCategory(message):
    if len(message.text) < 65:
        categories[message.text] = []
        bot.send_message(message.chat.id, toString(categories))
    else:
        bot.send_message(message.chat.id, 'Название слишком длинное. Сократите его или уберите несколько смайликов.')
        bot.register_next_step_handler(message, appendCategory)

def changeHeading(message):
    global heading
    heading = message.text
    bot.send_message(message.chat.id, toString(categories))

bot.polling(none_stop=True)

'''def func(message):
    webbrowser.open('https://mdl.sch239.net/course/view.php?id=368')'''

'''@bot.message_handler(content_types=['photo']
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Перейти на сайт', url='https://mdl.sch239.net/course/view.php?id=368'))

    bot.send_message(message.chat.id, f'hello {message.from_user.first_name} {message.from_user.last_name}')

    bot.send_message(message.chat.id, '<b>here</b> <em>you</em> <u>go</u>', parse_mode='html')

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
    bot.reply_to(message, f'ID: {message.from_user.id}')'''
