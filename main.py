import telebot
import datetime
import time
import threading
import random
from telebot import types

bot = telebot.TeleBot('Введите ваш токен')

# Словарь для хранения времени отхода ко сну и продолжительности сна для каждого пользователя
user_sleep_times = {}
user_sleep_durations = {}

# Список фактов о сне
facts = [
    "Сон состоит из двух основных фаз:\n\nМедленная фаза (сон Non-REM)\nЗанимает почти 75% от всей продолжительности сна. Состоит она из дремоты, легкой стадии и глубокой. Если на вторую стадию приходится около 20 минут, то на третью – 90 минут\n\nБыстрая фаза (REM-сон)\nНаступает после глубокой стадии медленной фазы. Сопровождается быстрым движением глаз (БДГ). Мозг в этот период активен практически так же, как и во время бодрствования. Именно при REM-сне человек видит наиболее яркие и осмысленные сновидения",
    "Во сне сделаны многие открытия и придуманы великие вещи\nМенделеев во сне увидел таблицу химических элементов, Ларри Пейдж – идею Google, изобретатель Элиас Хоу – швейную машинку. Пушкин во сне видел стихи. Сон подарил Полу Маккартни мелодию и аккорды песни Yesterday. Нильсу Бору во сне явилась структура атома, химику Фридриху Кекуле – формула бензола. Рихард Вагнер услышал во сне оперу «Тристан и Изольда». Бетховен во сне сочинил пьесу «Сон в летнюю ночь»",
    "Люди видят сны даже до рождения\nУченые предполагают, что сны человеческих эмбрионов из-за отсутствия визуальных стимулов в чреве матери в основном состоят из звуков и тактильных ощущений",
    "Порой нам кажется, что во сне мы видим незнакомых людей. Однако, это не так. Научно доказано, что нам снятся только те люди, которых мы видели наяву хотя бы раз в жизни",
    "Во время сна мы закрепляем полученные знания\nПока мы спим, наш мозг работает. Во время сна он переносит информацию из кратковременной памяти в долговременную. Вот почему человек, который мало спит, не может учиться в полную силу. Знания просто не будут закрепляться!",
    "Большинство наших снов трудно запомнить\nВы никогда не задумывались, почему вы не можете вспомнить свои сны большую часть времени? Не каждая область нашего мозга перестает работать сразу же после того, как мы засыпаем, и одна из последних областей, которая отключается, - это гиппокамп. Находясь под корой головного мозга, гиппокамп является важным компонентом мозга, который перемещает краткосрочную память в долгосрочную память. Если гиппокамп один из последних засыпает, он также может проснуться одним из последних. Итак, когда мы просыпаемся с памятью в нашей кратковременной памяти, наш мозг просто не может долго сохранять эту память, потому что гиппокамп по-прежнему неактивен."
]

# Словарь для хранения отправленных фактов для каждого пользователя
user_facts_sent = {}


@bot.message_handler(commands=['start'])
def send_message(message):
    bot.send_message(message.chat.id, 'Привет, Я SleepTracker бот! Я помогу тебе следить за распорядком сна!')


@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "Я SleepTracker бот! Вот список доступных команд:\n"
        "/start - Запуск бота и приветственное сообщение.\n"
        "/help - Показать список доступных команд и их описание.\n"
        "/newtracker - Выбор времени отхода ко сну и расчет продолжительности сна.\n"
        "/randomfact - Получить случайный факт о сне."
    )
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['newtracker'])
def new_tracker(message):
    msg = bot.reply_to(message, "Пожалуйста, введите время отхода ко сну в формате ЧЧ:ММ (например, 22:30):")
    bot.register_next_step_handler(msg, process_sleep_time)


def process_sleep_time(message):
    try:
        sleep_time = datetime.datetime.strptime(message.text, "%H:%M").time()
        user_sleep_times[message.chat.id] = sleep_time
        msg = bot.reply_to(message, "Пожалуйста, введите продолжительность сна в часах (например, 8):")
        bot.register_next_step_handler(msg, process_sleep_duration)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите время в правильном формате ЧЧ:ММ (например, 22:30).")


def process_sleep_duration(message):
    try:
        sleep_duration = float(message.text)
        user_sleep_durations[message.chat.id] = sleep_duration

        if 7 <= sleep_duration <= 9:
            send_wake_time(message.chat.id, user_sleep_times[message.chat.id], sleep_duration)
        else:
            markup = types.InlineKeyboardMarkup()
            yes_button = types.InlineKeyboardButton(f"Да, я хочу спать {sleep_duration} часов",
                                                    callback_data="confirm_yes")
            no_button = types.InlineKeyboardButton("Нет, введу другое количество часов", callback_data="confirm_no")
            markup.add(yes_button, no_button)
            bot.send_message(message.chat.id,
                             f"Уверены, что хотите спать именно {sleep_duration} часов? Достаточная продолжительность сна для взрослых людей составляет от 7 до 9 часов.",
                             reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное число часов.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_'))
def confirm_sleep_duration(call):
    chat_id = call.message.chat.id
    sleep_duration = user_sleep_durations[chat_id]
    if call.data == "confirm_yes":
        if sleep_duration < 7:
            bot.send_message(chat_id,
                             "Хорошо, но помните, недосып может привести к плохим последствиям относительно вашего здоровья!")
        else:
            bot.send_message(chat_id,
                             "Хорошо, но помните, постоянно длительный сон может плохо сказаться на вашем здоровье!")
        send_wake_time(chat_id, user_sleep_times[chat_id], sleep_duration)
    elif call.data == "confirm_no":
        bot.send_message(chat_id, "Пожалуйста, введите продолжительность сна в диапазоне от 7 до 9 часов.")
        msg = bot.send_message(chat_id, "Введите количество часов:")
        bot.register_next_step_handler(msg, process_sleep_duration)


def send_wake_time(chat_id, sleep_time, sleep_duration):
    wake_time = (datetime.datetime.combine(datetime.date.today(), sleep_time) + datetime.timedelta(
        hours=sleep_duration)).time()
    bot.send_message(chat_id,
                     f"Если ты ляжешь спать в {sleep_time.strftime('%H:%M')}, то тебе нужно будет проснуться в {wake_time.strftime('%H:%M')}, чтобы поспать {sleep_duration} часов.")


@bot.message_handler(commands=['randomfact'])
def send_random_fact(message):
    chat_id = message.chat.id
    if chat_id not in user_facts_sent:
        user_facts_sent[chat_id] = []

    if len(user_facts_sent[chat_id]) == len(facts):
        user_facts_sent[chat_id] = []

    remaining_facts = list(set(range(len(facts))) - set(user_facts_sent[chat_id]))
    fact_index = random.choice(remaining_facts)
    user_facts_sent[chat_id].append(fact_index)

    bot.send_message(chat_id, facts[fact_index])


def send_reminders():
    while True:
        now = datetime.datetime.now().time()
        for chat_id, sleep_time in user_sleep_times.items():
            reminder_time = (datetime.datetime.combine(datetime.date.today(), sleep_time) - datetime.timedelta(
                minutes=10)).time()
            if now.hour == reminder_time.hour and now.minute == reminder_time.minute:
                bot.send_message(chat_id,
                                 f"Время уже {reminder_time.strftime('%H:%M')}, пора ложиться спать! Твое время отхода ко сну: {sleep_time.strftime('%H:%M')}.")
                time.sleep(60)
        time.sleep(1)


#Поток для отправки напоминаний
reminder_thread = threading.Thread(target=send_reminders)
reminder_thread.start()

bot.polling(none_stop=True)





