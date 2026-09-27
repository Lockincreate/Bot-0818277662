import os
import threading
from flask import Flask
import telebot

# Tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot-0818277662 LIVE - Durban Hellodata SA - R5 is R5"

@bot.message_handler(commands=['start','help','prices'])
def start_msg(m):
    txt = """🔥 *HELLODATA SA - R5 is R5*
📍 Durban | WhatsApp: 0818277662

*BIG GIGZ - Telkom/MTN:*
1GB - R75
5GB - R149
10GB - R199
20GB - R349
50GB - R699

*How to Order:*
Send: `10GB 0821234567`

*Pay:*
Capitec: 0818277662
Reference: Your number

✅ Delivery in 5min after POP!
"""
    bot.send_message(m.chat.id, txt, parse_mode='Markdown')

@bot.message_handler(func=lambda x: True)
def all_handler(m):
    bot.reply_to(m, f"✅ Got: {m.text}\n\nPay Capitec 0818277662\nSend POP here. Deliver 5min!\n\nFast: WA 0818277662")

def run_telegram():
    print("Telegram Bot Starting...")
    bot.infinity_polling()

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_telegram, daemon=True).start()
    run_web()
import threading
@app.route('/')
def h(): return "ok"
threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
