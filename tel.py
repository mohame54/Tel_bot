import telebot
from workflow import AgenticChatWorkflow
from whisper import WhisperConfig, WhisperInference, download_models
import argparse


SYS_P = """You are a helpful Ai assistant which answers questions based on user quries,
if your don't have the sufficient knowledge to answer you should answer only with a proper keyword with specified parameters seperated between the two angle brackets according to the rules given please follow them carefully
<rules>
SEARCH_ARTICLE<article_subject>: if the user enters a prompt and you need some knowledge to asses your answer, article_subject: refers to the wanted article subject that the user asked about.
GENERATE_CODE<code_docs>: if the user enters a prompt that asks you to write code and you are not sure about some certain libraries and need some docummentation to asses your knowledge for generating code, code_docs: refers to the required code documentations to generate user wanted code could be multiple names seperated by a comma.
SAVE_CODE <script_name>: if the user asks you to generate code and you have the sufficient knowledge to do so, script_name: referes to conventional name for the wanted code.
</rules>
REMEMBER:
  If the knowledge is provided for you somehow including from the user side this should be sufficient for you to generate an answer.
  if you have to follow the rules you should only to answer with a keyword with the specified parameters.
if you do have the knowledge you don't have to follow the rules and give a clear and concise answer unless the user asks you to generate code then you should follow the above rules.
"""


parser = argparse.ArgumentParser()
parser.add_argument('--bot_tok', type=str, help='your telegram bot token')
parser.add_argument('--bot_name', type=str, help='your telegram bot name')
parser.add_argument('--chat_tok', type=str, help='Open Ai ChatGpt Api token')
parser.add_argument('--voice_model_dir', type=str, help='models for transcribing the voice messages into texts')
args = parser.parse_args()


# Initialize your telegram bot.
bot = telebot.TeleBot(args.bot_tok)
Chat = AgenticChatWorkflow(args.chat_tok)

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
        I 'm an AI assistant How can i help you?\
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
    text = Chat(text)        
    bot.reply_to(message, text)


@bot.message_handler(content_types=['voice'])
def repl_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('sound.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
    text = Transcriber("sound.ogg")[0]
    text = Chat(text)       
    bot.reply_to(message, text)


if __name__ == '__main__':
   print("Polling has begun!")
   bot.polling()
       