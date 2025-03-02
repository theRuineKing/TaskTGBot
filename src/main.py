import time
import telebot
import webbrowser
from telebot import types
from telebot.types import InlineKeyboardMarkup

botKey = '7760507421:AAFQ2xUSEf8T78A6MrB7aHaexz-2BaOcDGg'
bot = telebot.TeleBot(botKey)

heading = ''

global chatID
global dailyMessageID
dailyMessageID = 0
messages_to_delete = []

categories = {
    'Категория 1': ['task1', 'task2'],
    'Категория 2': ['task3', 'task4']
}

def toString(slovar):
    if dailyMessageID != 0: bot.delete_message(chatID, dailyMessageID)
    result = ''
    if heading != '':
        result += heading + '\n\n'
    for key in slovar:
        result += key + '\n'
        for item in slovar[key]:
            result += '- ' + item + '\n'
        result += '\n'

    return result

def addToDeleteList(message):
    messages_to_delete.append(message)

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

@bot.message_handler(commands=['start'])
def helloWorld(message):
    addToDeleteList(message)
    global chatID
    chatID = message.chat.id
    bot.send_message(message.chat.id, 'Привет! Это бот "Диспетчер задач". '
                                      'С его помощью вы можете:\n - отслеживать выполнение своих ежедневных и глобальных задач\n'
                                      ' - разделять их по категориям\n - отмечать их выполнение \n - устанавливать временной лимит и напоминания\n'
                                      ' - анализировать динамику своего прогресса, а также обращаться к полезным ресурсам по обучению и саморазвитию.')
    showProgress()

def showProgress():
    global dailyMessageID
    global chatID
    dailyMessageID = bot.send_message(chatID, toString(categories)).message_id
    for msg in messages_to_delete:
        try:
            bot.send_message(chatID, msg.text)
            messages_to_delete.remove(msg)
            bot.delete_message(chatID, msg.id)
        except Exception as e:
            print("", e)

@bot.message_handler(commands=['addcategorytask', 'renametask', 'deletetask', 'marktask'])
def operateWithTask(message):
    addToDeleteList(message)

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
    addToDeleteList(message)
    bot.send_message(message.chat.id, 'Введите название категории:')
    bot.register_next_step_handler(message, appendCategory)

@bot.message_handler(commands=['addheading'])
def addHeading(message):
    addToDeleteList(message)
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