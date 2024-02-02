import telebot
from chat import chat_from_sys


BOT_TOKEN = "6652869313:AAHlJq4_qQHN_mo_8fD_5EUNj7d8LGXBjTY"
BOT_USERNAME = "@sahm_sahm_bot"

bot = telebot.TeleBot(BOT_TOKEN)
Model = chat_from_sys(bot)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
Hi there, I am Sahm.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")

@bot.message_handler(commands=["end"])
async def send_welcome(message):
    Model.setup()
    await bot.reply_to(message, "released the conversation")

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    mssg_type = message.chat.type
    text = message.text
    if mssg_type == "group":
        if BOT_USERNAME in text:
            text = text.replace(BOT_USERNAME, "").strip()
        else:
            return
    output_text = Model.invoke(text)
    bot.reply_to(message, output_text)


if __name__ == '__main__':
   bot.polling()    