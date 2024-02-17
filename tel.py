import telebot
from chat import chat_from_key
from whisper import WhisperConfig, WhisperInference, download_models
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--bot_tok', type=str, help='your telegram bot token')
parser.add_argument('--bot_name', type=str, help='your telegram bot name')
parser.add_argument('--chat_tok', type=str, help='Open Ai ChatGpt Api token')
parser.add_argument('--voice_model_dir', type=str, help='models for transcribing the voice messages into texts')
args = parser.parse_args()


# Initialize your telegram bot.
bot = telebot.TeleBot(args.bot_tok)
Chat = chat_from_key(args.chat_tok)

# Download and Prepare the Pretrained Models for transcribing the voice messages.
download_models(args.voice_model_dir)
encoder_path = f"{args.voice_model_dir}/encoder.int8.onnx"
decoder_path = f"{args.voice_model_dir}/decoder.int8.onnx"
config = WhisperConfig(
    encoder_path,
    decoder_path,
)
Transcriber = WhisperInference(config)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def start_mssg(message):
    Chat.setup()
    bot.reply_to(message, """\
        Hi there, I am Sahm.
        I 'm an AI assistant who can help you study!\
    """)
                                    

@bot.message_handler(commands=["end"])
def end_mssg(message):
    Chat.setup()
    bot.reply_to(message, "released the conversation")


@bot.message_handler(func=lambda message: True)
def repl_message(message):
    mssg_type = message.chat.type
    text = message.text
    if mssg_type == "group":
        if args.bot_name in text:
            text = text.replace(args.bot_name, "").strip()
        else:
            return       
    text = Chat.invoke(text)        
    bot.reply_to(message, text)


@bot.message_handler(content_types=['voice'])
def repl_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('sound.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
    text = Transcriber("sound.ogg")[0]
    text = Chat.invoke(text)       
    bot.reply_to(message, text)


if __name__ == '__main__':
   bot.polling()
       