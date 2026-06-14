import threading
import requests
import telebot
from telebot import types
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- НАСТРОЙКИ ---
TELEGRAM_BOT_TOKEN = "8364020564:AAFHjktRvP45PVU-lKX7OjD8tlwc_Q1pRic"
TELEGRAM_CHAT_ID = "529651568"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# --- ЛОГИКА УВЕДОМЛЕНИЙ С САЙТА ---
def send_telegram_notification(name, phone, car, service):
    message = (
        f"🔥 <b>Новая заявка с сайта детейлинга!</b>\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📞 <b>Телефон:</b> {phone}\n"
        f"🚗 <b>Автомобиль:</b> {car}\n"
        f"🛠 <b>Услуга:</b> {service}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка отправки: {e}")


# --- ЛОГИКА ТЕЛЕГРАМ БОТА (ОТВЕТЫ ПОЛЬЗОВАТЕЛЯМ) ---
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_services = types.KeyboardButton("🛠 Наши услуги")
    btn_game = types.KeyboardButton("🏎 Играть и получить скидку")
    btn_contacts = types.KeyboardButton("📞 Контакты")
    markup.add(btn_services, btn_game, btn_contacts)

    welcome_text = f"Cześć, {message.from_user.first_name}! 👋\nДобро пожаловать в нашу студию детейлинга!"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "🛠 Наши услуги":
        bot.send_message(message.chat.id, "🔥 <b>Услуги:</b>\n1. Керамика ✨\n2. Полировка 🚗\n3. Химчистка 🧼",
                         parse_mode="HTML")
    elif message.text == "🏎 Играть и получить скидку":
        # Ссылку ниже мы заменим на настоящую, когда сервер выдаст её нам!
        bot.send_message(message.chat.id, "Запустите игру на нашем сайте: Ссылка будет тут!")
    elif message.text == "📞 Контакты":
        bot.send_message(message.chat.id, "📍 Познань, Польша\n📱 +48 XXX XXX XXX", parse_mode="HTML")


# Функция для запуска бота в отдельном потоке
def run_bot():
    print("--- Фоновый бот запущен ---")
    bot.infinity_polling(non_stop=True)


# --- РОУТЫ ВЕБ-САЙТА ---
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/join', methods=['POST'])
def join():
    name = request.form.get('name')
    phone = request.form.get('phone')
    car = request.form.get('car')
    service = request.form.get('service')
    send_telegram_notification(name, phone, car, service)
    return redirect(url_for('thanks'))


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


# Запускаем бота ОДНОВРЕМЕННО с запуском сайта Flask
if __name__ != '__main__':
    # Этот блок сработает на удаленном сервере Render
    threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    # Этот блок работает, когда ты тестируешь локально в PyCharm
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(debug=True)