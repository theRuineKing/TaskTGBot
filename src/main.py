import telebot
from telebot import types

import sqlite3
import json

from datetime import datetime, timedelta
import time
import threading

botKey = '7586335552:AAE-r3zVg4Mviutm44-UbjZBEqnFunEGgHY'
bot = telebot.TeleBot(botKey)

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


def toString(slovar):
    today = datetime.now()
    result = f'{today.day} {months[today.month]} {today.year} года\n\n'

    for key in slovar:
        result += key + '\n'
        for item in slovar[key]:
            result += '- ' + item + '\n'
        result += '\n'
    return result

def checkDay():
    if datetime.now().strftime('%H') == '00':
        with open('data.txt', 'r') as file:
            head = json.load(file)

        conn = sqlite3.connect('plannedTasks.sql')
        cur = conn.cursor()

        cur.execute(
            'CREATE TABLE IF NOT EXISTS plannedtasks (id int auto_increment primary key, '
            'userID integer(10), date varchar(10), task varchar(100))')
        for ID in head:
            cur.execute("SELECT * FROM plannedtasks WHERE userID=? AND date = ?", (ID, datetime.now().strftime('%d.%m.%Y'),))
            tasks = cur.fetchall()

            head[ID] = {}
            head[ID]["Запланированные задачи"] = []
            for task in tasks:
                head[ID]["Запланированные задачи"].append(task[3])
            bot.send_message(ID, toString(head[ID]))
            bot.send_message(ID, 'Задачи обновлены')

            cur.execute("DELETE FROM plannedtasks WHERE userID = ? AND date = ?",
                        (ID, datetime.now().strftime('%d.%m.%Y'),))

        conn.commit()
        cur.close()
        conn.close()
        with open('data.txt', 'w') as file:
            # noinspection PyTypeChecker
            json.dump(head, file)
    else:
        print('checking')

def run_every_n_minutes(minutes, action, *args):
    threading.Timer(minutes, run_every_n_minutes, [minutes, action] + list(args)).start()
    action(*args)
run_every_n_minutes(3600, checkDay)


@bot.message_handler(commands=['start'])
def helloWorld(message):
    ID = str(message.from_user.id)
    with open('data.txt', 'r') as file:
        head = json.load(file)

    if ID not in head:
        head[ID] = {'Ваша категория 1': ['Ваша задача 1', 'Ваша задача 2'],
                    'Ваша категория 2': ['Ваша задача 3', 'Ваша задача 4']}

        with open('data.txt', 'w') as file:
            # noinspection PyTypeChecker
            json.dump(head, file)

    bot.send_message(message.chat.id, toString(head[ID]))
    bot.send_message(message.chat.id, 'Привет! Это бот "Диспетчер задач".')


days = {
    'Monday': 'Понедельник',
    'Tuesday': 'Вторник',
    'Wednesday': 'Среда',
    'Thursday': 'Четверг',
    'Friday': 'Пятница',
    'Saturday': 'Суббота',
    'Sunday': 'Воскресенье'
}

@bot.message_handler(commands=['plantask'])
def planTask(message):
    markup = types.ReplyKeyboardMarkup()

    btns = []
    today = datetime.now()

    for i in range(1, 9):
        delta = (today + timedelta(days=i)).strftime("%d.%m.%Y")
        date_object = datetime.strptime(delta, "%d.%m.%Y")
        if i == 1:
            btns.append(types.KeyboardButton(delta+' (Завтра)'))
        elif i == 2:
            btns.append(types.KeyboardButton(delta+' (Послезавтра)'))
        else:
            btns.append(types.KeyboardButton(delta+f' ({days[date_object.strftime("%A")]})'))
    i = 0
    while i <= 3:
        markup.row(btns[i], btns[i+4])
        i += 1

    bot.reply_to(message, 'Введите дату в формате ДД.ММ.ГГГГ, или выберите из предложенных:', reply_markup=markup)
    bot.register_next_step_handler(message, chooseDate)

daysInMonths = {
    1: 3,
    2: 'февраль',
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}


def is_leap(year):
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False

def checkDate(date):
    year = int(date[6:10])
    currentYear = int(datetime.now().strftime('%Y'))
    month = int(date[3:5])
    currentMonth = int(datetime.now().strftime('%m'))
    day = int(date[0:2])
    currentDay = int(datetime.now().strftime('%d'))

    if year == 0:
        return False
    elif month > 12:
        return False
    elif month == 2:
        if is_leap(year) and day > 29:
            return False
        if not is_leap(year) and day > 28:
            return False
    elif day > daysInMonths[currentMonth]:
        return False
    elif year < currentYear:
        return False
    elif year == currentYear and month < currentMonth:
        return False
    elif year == currentYear and month == currentMonth and day <= currentDay:
        return False
    return True

def chooseDate(message):
    text = message.text
    if len(text) >= 10:
        if text[0:2].isdigit() and text[2] == '.' and text[3:5].isdigit() and text[5] == '.' and text[6:10].isdigit():
            if checkDate(text[0:10]):
                bot.send_message(message.chat.id, 'Введите задачу:')
                bot.register_next_step_handler(message, chooseTask, text[0:10])
            else:
                bot.send_message(message.chat.id, 'Такой даты нет, или она уже прошла. Проверьте ввод и попробуйте ещё раз.')
                bot.register_next_step_handler(message, chooseDate)
        else:
            bot.send_message(message.chat.id, 'Неверный формат даты, введите ещё раз.')
            bot.register_next_step_handler(message, chooseDate)
    else:
        bot.send_message(message.chat.id, 'Неверный формат даты, введите ещё раз.')
        bot.register_next_step_handler(message, chooseDate)

def chooseTask(message, date):
    ID = message.from_user.id
    conn = sqlite3.connect('plannedTasks.sql')
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS plannedtasks (id int auto_increment primary key, '
        'userID integer(10), date varchar(10), task varchar(100))')
    cur.execute("INSERT INTO plannedtasks (userID, date, task) VALUES ('%i', '%s', '%s')" % (ID, date, message.text))

    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Задача запланирована')

def getArray(ID):
    conn = sqlite3.connect('plannedTasks.sql') #открывает соединение с бд
    cur = conn.cursor() #создает курсор

    cur.execute(
        'CREATE TABLE IF NOT EXISTS plannedtasks (id int auto_increment primary key, '
        'userID integer(10), date varchar(10), task varchar(100))') #создает таблицу
    cur.execute("SELECT * FROM plannedtasks WHERE userID=?", (ID,)) #выбирает нужные записи
    tasks = cur.fetchall() #объединяет их в массив

    arr = []
    for i in range(len(tasks)):
        date = tasks[i][2]
        task = tasks[i][3]
        if i == 0:
            arr.append([date, task])
        else:
            arr.append([date, task])
            j = len(arr) - 2
            while j >= 0:
                if datetime.strptime(arr[j][0], "%d.%m.%Y") > datetime.strptime(date, "%d.%m.%Y"):
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                else:
                    break
                j -= 1
    cur.close() #закрывает курсор
    conn.close() #закрывает соединение с бд
    return arr

@bot.message_handler(commands=['showplannedtasks'])
def showPlannedTasks(message):
    ID = message.from_user.id

    info = ''
    prevDate = '00.00.0000'
    for task in getArray(ID):
        if task[0] != prevDate:
            date = datetime.strptime(task[0], "%d.%m.%Y")
            info += f'\n{task[0]} ({days[date.strftime("%A")]}):\n  - {task[1]}\n'
        else:
            info += f'  - {task[1]}\n'
        prevDate = task[0]

    if info != '':
        bot.send_message(message.chat.id, info)
    else:
        bot.send_message(message.chat.id, 'Нет запланированных задач')

@bot.message_handler(commands=['deleteallplans'])
def deleteAllPlans(message):
    conn = sqlite3.connect('plannedTasks.sql')
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS plannedtasks (id int auto_increment primary key, '
        'userID integer(10), date varchar(10), task varchar(100))')
    sql_delete_query = f'DELETE from plannedtasks where userID = {message.from_user.id}'
    cur.execute(sql_delete_query)

    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Запланированные задачи удалены')

@bot.message_handler(commands=['deleteplannedtask'])
def deletePlannedTask(message):
    ID = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    btns = []
    arr = getArray(ID)

    if arr:
        for task in arr:
            btns.append(types.InlineKeyboardButton(task[0] + ': ' + task[1], callback_data='t' + task[0] + task[1]))
        for btn in btns:
            markup.row(btn)
        bot.reply_to(message, 'Выберите задачу:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Нет запланированных задач')


@bot.message_handler(commands=['addtask', 'renametask', 'deletetask', 'marktask', 'renamecategory', 'deletecategory'])
def operateWithTask(message):
    markup = types.InlineKeyboardMarkup()
    with open('data.txt', 'r') as file:
        head = json.load(file)
    categories = head[str(message.from_user.id)]

    btns = []
    if message.text == '/addtask':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='1' + key))
    elif message.text == '/renametask':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='2' + key))
    elif message.text == '/deletetask':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='4' + key))
    elif message.text == '/marktask':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='6' + key))
    elif message.text == '/renamecategory':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='8' + key))
    elif message.text == '/deletecategory':
        for key in categories: btns.append(types.InlineKeyboardButton(key, callback_data='9' + key))

    for btn in btns:
        markup.row(btn)
    bot.reply_to(message, 'Выберите категорию:', reply_markup=markup)


@bot.message_handler(commands=['addcategory'])
def addCategory(message):
    bot.send_message(message.chat.id, 'Введите название категории:')
    bot.register_next_step_handler(message, appendCategory)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    ID = str(callback.from_user.id)
    key = callback.data[1:]
    with open('data.txt', 'r') as file:
        head = json.load(file)

    if callback.data[0] == '1':
        bot.send_message(callback.message.chat.id, 'Введите задачу:')
        bot.edit_message_text(key, callback.message.chat.id, callback.message.message_id)
        bot.register_next_step_handler(callback.message, appendTask, key)

    elif (callback.data[0] == '2' or callback.data[0] == '4' or callback.data[0] == '6'
          or callback.data[0] == '8' or callback.data[0] == '9'):
        markup = types.InlineKeyboardMarkup()
        btns = []
        if callback.data[0] == '2':
            for i in range(len(head[ID][key])):
                btns.append(types.InlineKeyboardButton(head[ID][key][i], callback_data='3' + str(i) + '|' + key))
            for btn in btns:
                markup.row(btn)
            bot.reply_to(callback.message, 'Выберите задачу, которую хотите переименовать:', reply_markup=markup)
        if callback.data[0] == '4':
            for i in range(len(head[ID][key])):
                btns.append(types.InlineKeyboardButton(head[ID][key][i], callback_data='5' + str(i) + '|' + key))
            for btn in btns:
                markup.row(btn)
            if btns:
                bot.reply_to(callback.message, 'Выберите задачу, которую хотите удалить:', reply_markup=markup)
            else:
                bot.send_message(callback.message.chat.id, 'Категория пуста')
        elif callback.data[0] == '6':
            for i in range(len(head[ID][key])):
                btns.append(types.InlineKeyboardButton(head[ID][key][i], callback_data='7' + str(i) + '|' + key))
            for btn in btns:
                markup.row(btn)
            bot.reply_to(callback.message, 'Выберите задачу:', reply_markup=markup)
        elif callback.data[0] == '8':
            bot.send_message(callback.message.chat.id, 'Введите новое название категории:')
            bot.register_next_step_handler(callback.message, renameCategory, key)
        elif callback.data[0] == '9':
            del head[ID][key]
            bot.send_message(ID, toString(head[ID]))
            with open('data.txt', 'w') as file:
                # noinspection PyTypeChecker
                json.dump(head, file)

    elif callback.data[0] == '3':
        bot.send_message(callback.message.chat.id, 'Введите новое название задачи:')
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.register_next_step_handler(callback.message, renameTask,
                                       callback.data[callback.data.index('|') + 1:],
                                       int(callback.data[1:callback.data.index('|')]))

    elif callback.data[0] == '5':
        with open('data.txt', 'r') as file:
            head = json.load(file)
        head[ID][callback.data[callback.data.index('|') + 1:]].pop(int(callback.data[1:callback.data.index('|')]))
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(ID, toString(head[ID]))
        with open('data.txt', 'w') as file:
            # noinspection PyTypeChecker
            json.dump(head, file)

    elif callback.data[0] == '7':
        i = int(callback.data[1:callback.data.index('|')])
        key = callback.data[callback.data.index('|') + 1:]

        with open('data.txt', 'r') as file:
            head = json.load(file)
        task = head[ID][key][i]

        if task[0] == '✅':
            head[ID][key][i] = '❌' + head[ID][key][i][1:]
        elif task[0] == '❌':
            head[ID][key][i] = '✅' + head[ID][key][i][1:]
        else:
            head[ID][key][i] = '✅ ' + task

        bot.send_message(ID, toString(head[ID]))
        with open('data.txt', 'w') as file:
            # noinspection PyTypeChecker
            json.dump(head, file)

    elif callback.data[0] == 't':
        date = callback.data[1:11]
        task = callback.data[11:]

        conn = sqlite3.connect('plannedTasks.sql')
        cur = conn.cursor()

        cur.execute(
            'CREATE TABLE IF NOT EXISTS plannedtasks (id int auto_increment primary key, '
            'userID integer(10), date varchar(10), task varchar(100))')

        cur.execute('DELETE FROM plannedtasks WHERE userID = (?) AND date = (?) AND task = (?)',
                    (ID, date, task,))

        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(ID, 'Задача удалена.')


def appendTask(message, key):
    ID = str(message.from_user.id)
    with open('data.txt', 'r') as file:
        head = json.load(file)
    head[ID][key].append(message.text)
    bot.send_message(ID, toString(head[ID]))
    with open('data.txt', 'w') as file:
        # noinspection PyTypeChecker
        json.dump(head, file)


def renameTask(message, key, i):
    ID = str(message.from_user.id)
    with open('data.txt', 'r') as file:
        head = json.load(file)

    head[ID][key][i] = message.text
    bot.send_message(ID, toString(head[ID]))
    with open('data.txt', 'w') as file:
        # noinspection PyTypeChecker
        json.dump(head, file)


def appendCategory(message):
    if len(message.text) < 65:
        ID = str(message.from_user.id)
        with open('data.txt', 'r') as file:
            head = json.load(file)

        if message.text in head[ID]:
            bot.send_message(message.chat.id, 'Такая категория уже существует. Попробуйте другое название.')
            bot.register_next_step_handler(message, appendCategory)
        else:
            head[str(ID)][message.text] = []
            bot.send_message(ID, toString(head[ID]))
            with open('data.txt', 'w') as file:
                # noinspection PyTypeChecker
                json.dump(head, file)
    else:
        bot.send_message(message.chat.id, 'Название слишком длинное. Сократите его или уберите несколько смайликов.')
        bot.register_next_step_handler(message, appendCategory)

def renameCategory(message, key):
    ID = str(message.from_user.id)
    with open('data.txt', 'r') as file:
        head = json.load(file)

    head[ID][message.text] = head[ID][key]
    del head[ID][key]

    bot.send_message(ID, toString(head[ID]))
    with open('data.txt', 'w') as file:
        # noinspection PyTypeChecker
        json.dump(head, file)

commands = ['/start', '/addtask', '/renametask', '/marktask', '/deletetask', '/addcategory', '/renamecategory',
            '/deletecategory', '/plantask', '/showplannedtasks', '/deleteplannedtask', '/deleteallplans']

@bot.message_handler()
def isRubbish(message):
    if message.text not in commands:
        bot.delete_message(message.chat.id, message.message_id)
        sentmessage = bot.send_message(message.chat.id, 'Вы ввели неверную команду')
        time.sleep(5)
        bot.delete_message(message.chat.id, sentmessage.message_id)

bot.polling()