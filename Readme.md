# Building a Telegram ChatBot 
### This an implementation of a telegram Chatbot using Langchain and a Speech to text Whisper optimized for inference. 

## Features
**ASR Model**: employing an optimized version of  Whisper ASR model for inference and deployment.

**LangChain and OpenAi**: Utilizing The powerful **LangChain** framework to create an easy to implement a chatbot using OpenAi API.

**Deployment and Inference**: ONNX Runtime is utilized for efficient model inference.


## Getting Started
### Installation:

**Clone this repository to your local machine Install the required dependencies using** `pip`
```bash
pip install -r requirements.txt
```
## Run python script:

## How to run your telgram bot:
*you can use ***CLI*** to show your options*
> python train.py -h   **To show the available command**

*you should provide some **Parameters** in order for the script to work**
> python tel.py --bot_tok <your_bot_token> --bot_name <your_bot_name> --chat_tok <your_openai_api_key> --voice_model_dir <the_directory_where_to_save_the_downloaded_transcriber>

*This ***command*** will create and run your chatbot in `telegram` and after that you can use it freely.*
