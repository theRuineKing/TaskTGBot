import telebot
#import webbrowser
from telebot import types
import sqlite3
from datetime import datetime
import slovari
import json

#import schedule
import time
import threading

botKey = '7760507421:AAFQ2xUSEf8T78A6MrB7aHaexz-2BaOcDGg'
bot = telebot.TeleBot(botKey)

heading = '' #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#global chatID

categories = {
    'Категория 1': ['task1', 'task2'],
    'Категория 2': ['task3', 'task4']
}

months = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря'
}

currentDate = None #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
lastDate = None #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def checkDay(): #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    global chatID
    global lastDate
    global currentDate

    currentDate = datetime.now().strftime('%Y-%m-%d')
    if currentDate != lastDate:
        bot.send_message(chatID, currentDate)
        lastDate = currentDate

    threading.Timer(10, checkDay).start()


def toString(slovar):
    today = datetime.now() #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    result = f'{today.day} {months[today.month]} {today.year} года\n\n' #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    if heading != '':
        result += heading + '\n\n'
    for key in slovar:
        result += key + '\n'
        for item in slovar[key]:
            result += '- ' + item + '\n'
        result += '\n'
    return result

#def addToDeleteList(message):
 #   messages_to_delete.append(message)

'''@bot.message_handler(commands=['deletemess'])
def deleteMessages():
    for msg in messages_to_delete:
        messages_to_delete.append(msg.message_id)

    for msg_id in messages_to_delete:
        try:
            bot.delete_message(chat_id, msg_id)
        except Exception as e:
            print("", e)'''

commands = ['/start', '/addheading','/addcategorytask','/addtask','/renametask','/marktask','/deletetask',
            '/addcategory','/renamecategory','/deletecategory', '/deleteheading']

ids = []

@bot.message_handler(commands=['start'])
def helloWorld(message):
    id = message.from_user.id
    userDict = f'slovarOfUser{id}'
    if id not in ids:
        ids.append(id)
        with open('slovari.py', 'w') as file:
            file.write(userDict + ' = ')
            json.dump(categories, file)
    from slovari import userDict
    print(ids)
    from my_dict import my_dict

    '''global lastDate

    if lastDate is None:
        global currentDate
        currentDate = datetime.now().minute
        # для проверки даты:        .strftime('%Y-%m-%d')
        lastDate = currentDate
        bot.send_message(chatID, 'timer started')
        checkDay()'''

    conn = sqlite3.connect(f'Table{str(message.from_user.id)}.sql') # открывает соединение с бд
    cur = conn.cursor() # создаёт курсор

    cur.execute(
        f'CREATE TABLE IF NOT EXISTS Table{str(message.from_user.id)} (id int auto_increment primary key, date varchar(10), task varchar(100))')

    conn.commit()  # синхронизируем команду ^ с бд
    cur.close()  # закрывает курсор
    conn.close() #закрыват соединение с бд

    #user_date = message.date
    #bot.send_message(chatID, user_date)
    bot.send_message(chatID, 'Привет! Это бот "Диспетчер задач". '
                                      'С его помощью вы можете:\n - отслеживать выполнение своих ежедневных и глобальных задач\n'
                                      ' - разделять их по категориям\n - отмечать их выполнение \n - устанавливать временной лимит и напоминания\n'
                                      ' - анализировать динамику своего прогресса, а также планировать задачи на любой день вперёд.')
    showProgress()

@bot.message_handler(commands=['plantask'])
def planTask(message):
    bot.send_message(message.chat.id, 'Введите дату в формате ДД.ММ:')
    bot.register_next_step_handler(message, chooseDate)

def chooseDate(message):
    text = message.text
    if text[0:2].isdigit() and text[2] == '.' and text[3:5]:
        date = message.text.strip()
        bot.send_message(message.chat.id, 'Введите задачу:')
        bot.register_next_step_handler(message, chooseTask, date)
    else:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, 'Неверный формат даты')

def chooseTask(message, date):
    conn = sqlite3.connect('plannedTasks.sql')  # открывает соединение с бд
    cur = conn.cursor()  # создаёт курсор

    cur.execute(
        'CREATE TABLE IF NOT EXISTS plannedtasks (id int auto_increment primary key, '
        'date varchar(10), task varchar(100))')
    cur.execute("INSERT INTO plannedtasks (date, task) VALUES ('%s', '%s')" % (date, message.text))

    conn.commit()  # синхронизируем команду ^ с бд
    cur.close()  # закрывает курсор
    conn.close()  # закрыват соединение с бд

    bot.send_message(message.chat.id, 'Задача запланирована')


@bot.message_handler(commands=['showplannedtasks'])
def showPlannedTasks(message):
    conn = sqlite3.connect('plannedTasks.sql')  # открывает соединение с бд
    cur = conn.cursor()  # создаёт курсор

    cur.execute('SELECT * FROM plannedtasks')
    tasks = cur.fetchall()  # возвращает все найденные записи

    info = ''
    for task in tasks:
        info += f'Дата: {task[1]}, задача: {task[2]}\n'

    cur.close()  # закрывает курсор
    conn.close()  # закрыват соединение с бд

    if info != '':
        bot.send_message(message.chat.id, info)
    else:
        bot.send_message(message.chat.id, 'Нет запланированных задач')


@bot.message_handler(commands=['deleteallplans'])
def deleteAllPlans(message):
    conn = sqlite3.connect('plannedTasks.sql')  # открывает соединение с бд
    cur = conn.cursor()  # создаёт курсор

    cur.execute("DROP TABLE plannedtasks")
    cur.execute(
        'CREATE TABLE IF NOT EXISTS plannedtasks (id int auto_increment primary key, '
        'date varchar(10), task varchar(100))')

    cur.close()  # закрывает курсор
    conn.close()  # закрыват соединение с бд

    bot.send_message(message.chat.id, 'Запланированные задачи удалены')

def showProgress():
    bot.send_message(chatID, toString(categories))

def send_delayed_message(message):
    bot.send_message(chatID, message)

#def schedule_message(message, delay):
#    schedule.every(delay).hours.do(send_delayed_message, message)

@bot.message_handler(commands=['addcategorytask', 'renametask', 'deletetask', 'marktask'])
def operateWithTask(message):
    markup = types.InlineKeyboardMarkup()

    btns = []
    if message.text == '/addcategorytask':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='1'+key))
    elif message.text == '/renametask':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='2'+key))
    elif message.text == '/deletetask':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='4'+key))
    elif message.text == '/marktask':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='6'+key))

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

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global chatID
    chatID = callback.message.chat.id

    key = callback.data[1:]
    if callback.data[0] == '1':
        bot.send_message(callback.message.chat.id, 'Введите задачу:')
        bot.register_next_step_handler(callback.message, appendTask, key)

    elif callback.data[0] == '2' or callback.data[0] == '4' or callback.data[0] == '6':
        markup = types.InlineKeyboardMarkup()
        btns = []
        if callback.data[0] == '2':
            for i in range(len(categories[key])):
                btns.append(types.InlineKeyboardButton(categories[key][i], callback_data='3' + str(i) + '|' + key))
            for btn in btns:
                markup.row(btn)
            bot.reply_to(callback.message, 'Выберите задачу, которую хотите переименовать:', reply_markup=markup)
        if callback.data[0] == '4':
            for i in range(len(categories[key])):
                btns.append(types.InlineKeyboardButton(categories[key][i], callback_data='5' + str(i) + '|' + key))
            for btn in btns:
                markup.row(btn)
            bot.reply_to(callback.message, 'Выберите задачу, которую хотите удалить:', reply_markup=markup)
        elif callback.data[0] == '6':
            for i in range(len(categories[key])):
                btns.append(types.InlineKeyboardButton(categories[key][i], callback_data='7' + str(i) + '|' + key))
            for btn in btns:
                markup.row(btn)
            bot.reply_to(callback.message, 'Выберите задачу:', reply_markup=markup)

    elif callback.data[0] == '3':
        bot.send_message(callback.message.chat.id, 'Введите новое название задачи:')
        bot.register_next_step_handler(callback.message, renameTask,
                                       callback.data[callback.data.index('|') + 1:],
                                       int(callback.data[1:callback.data.index('|')]))
    elif callback.data[0] == '5':
        bot.send_message(callback.message.chat.id, callback.data)
        deleteTask(callback.data[callback.data.index('|') + 1:],
                                       int(callback.data[1:callback.data.index('|')]))
    elif callback.data[0] == '7':
        markTask(callback.data[callback.data.index('|') + 1:],
                   int(callback.data[1:callback.data.index('|')]))

    #bot.edit_message_text('Edited text', callback.message.chat.id, callback.message.message_id)

def appendTask(message, key):
    categories[key].append(message.text)
    showProgress()

def renameTask(message, key, i):
    categories[key][i] = message.text
    showProgress()

def deleteTask(key, i):
    global chatID
    categories[key].pop(i)
    showProgress()

def markTask(key, i):
    global chatID
    categories[key][i] = '✅ ' + categories[key][i]
    showProgress()

def appendCategory(message):
    if len(message.text) < 65:
        categories[message.text] = []
        showProgress()
    else:
        bot.send_message(message.chat.id, 'Название слишком длинное. Сократите его или уберите несколько смайликов.')
        bot.register_next_step_handler(message, appendCategory)

def changeHeading(message):
    global heading
    heading = message.text
    showProgress()

@bot.message_handler(commands=['deleteheading'])
def deleteHeading(message):
    global heading
    heading = ''
    global chatID
    chatID = message.chat.id
    showProgress()

@bot.message_handler()
def isRubbish(message):
    if message.text not in commands:
        bot.delete_message(message.chat.id, message.message_id)
        sentmessage = bot.send_message(message.chat.id, 'Вы ввели неверную команду')
        time.sleep(5)
        bot.delete_message(message.chat.id, sentmessage.message_id)

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