import telebot
from telebot import types
import time
import threading

API_TOKEN = '7739685016:AAEZkA1dZ77pJ31TPPZGyal8CH0b22RZbgA'
bot = telebot.TeleBot(API_TOKEN)
STORAGE: dict = {'user': {'Status': 'isStart', 'Tasks': ['taskq', 'task2'], 'Command': 'None'}}
stop_event = threading.Event()
def send_delayed_message(chat_id: int, message: str, delay: int) -> None:
    time.sleep(delay)
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_save = telebot.types.InlineKeyboardButton(text="Да",
                                                     callback_data='ready')
    button_change = telebot.types.InlineKeyboardButton(text="Нет",
                                                       callback_data='cooldown')
    keyboard.add(button_save, button_change)
    bot.send_message(chat_id, message , reply_markup=keyboard)

def run_task(chat_id: int, command: str) -> None:
    try:
        stop_event.clear()
        delay = 25 if command == 'Начать' else 5  # Тестовый таймер
        # delay = 25*60 if command == 'Начать' else 5*60
        message = 'Успел?' if command == 'Запустить' else 'Начнем?'
        threading.Thread(target=send_delayed_message, args=(chat_id, message, delay)).start()
        STORAGE[chat_id]['Status'] = False
    except (ValueError, IndexError):
        bot.send_message(chat_id, "Ошибка")

def get_tasks(chat_id: int) -> str:
    global STORAGE
    tasks = STORAGE[chat_id]['Tasks']
    t = ''
    if tasks == []:
        t = '\nнет заданий'
    else:
        for i in STORAGE[chat_id]['Tasks']:
            t += '\n• ' + i
    return f"Задание на сегодня:{t}"

def add_task(chat_id: int, task_text: str) -> bool:
    global STORAGE
    try:
        STORAGE[chat_id]['Tasks'] += [task_text]
        bot.send_message(chat_id, "Напишите новую задачу")
        return True
    except(ValueError, IndexError):
        print(ValueError, IndexError)
        return False

def del_task(chat_id: int, task_index: int) -> bool:
    global STORAGE
    try:
        task = STORAGE[chat_id]['Tasks'][task_index - 1]
        STORAGE[chat_id]['Tasks'].pop(task_index - 1)
        bot.send_message(chat_id, f"Задача {task} удалена")
        return True
    except:
        return False

def finish_task(chat_id: int) -> bool:
    global stop_event, STORAGE
    try:
        stop_event.set()
        bot.send_message(chat_id, "Задача завершена")
        STORAGE[chat_id]['Status'] = True
        return True
    except:
        return False

@bot.message_handler(commands=['start'])
def start_message(message):
    global STORAGE
    chat_id = message.chat.id
    bot.send_message(chat_id, "Добро пожаловать в SeaTime")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Добавить"))
    markup.add(types.KeyboardButton("Запустить"))
    markup.add(types.KeyboardButton("Закончить"))
    markup.add(types.KeyboardButton("Удалить"))
    markup.add(types.KeyboardButton("Посмотреть"))
    bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'cooldown')
def cooldown(call):
    message = call.message
    chat_id = message.chat.id
    bot.send_message(chat_id, "5 минут на отдых")
    run_task(chat_id, message.text)

@bot.callback_query_handler(func=lambda call: call.data == 'ready')
def ready(call):
    message = call.message
    chat_id = message.chat.id
    bot.send_message(chat_id, "Выберите что вам надо")
    STORAGE[chat_id]['Status'] = True

@bot.message_handler(func=lambda message: True)
def bot_comand(message):
    global STORAGE
    chat_id = message.chat.id
    if not STORAGE.get(chat_id):
        STORAGE[chat_id] = {'Status': True, 'Tasks': [], 'Command': 'None'}
    if message.text == "Добавить":
        STORAGE[chat_id]['Command'] = 'add'
        bot.send_message(chat_id, "Напишите новую задачу")
    elif message.text == "Удалить":
        if STORAGE[chat_id]['Tasks'] != []:
            STORAGE[chat_id]['Command'] = 'del'
            bot.send_message(chat_id, "Напишите номер задачи для удаления")
        else:
            bot.send_message(chat_id, 'Задачи отутсвуют')
    elif message.text == "Запустить" and STORAGE[chat_id]['Status']:
        STORAGE[chat_id]['Command'] = 'None'
        if STORAGE[chat_id]['Tasks'] != []:
            run_task(chat_id, message.text)
        else:
            bot.send_message(chat_id, 'Задачи отутсвуют')
    elif message.text == "Посмотреть":
        STORAGE[chat_id]['Command'] = 'None'
        bot.send_message(chat_id, get_tasks(chat_id))
    elif message.text == "Закончить" and not STORAGE[chat_id]['Status']:
        STORAGE[chat_id]['Command'] = 'None'
        finish_task(chat_id)
    elif STORAGE[chat_id]['Command'] == 'add':
        add_task(chat_id, message.text)
    elif STORAGE[chat_id]['Command'] == 'del':
        try:
            del_task(chat_id, int(message.text))
        except:
            bot.send_message(chat_id, 'Введит номер задачи')

bot.polling()
