import textwrap
import json
import re
import os
from dotenv import load_dotenv
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import tiktoken
from openai import OpenAI
import google.generativeai as genai
import anthropic
from flask_cors import CORS
import json
from deepgram import Deepgram
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
deepgram = DeepgramClient(DEEPGRAM_API_KEY)


def transcribe_audio(audio_file):
    with open(audio_file, "rb") as file:
        buffer_data = file.read()

    payload = {
        "buffer": buffer_data,
    }
    options = {
        "model": "nova-2",
        "smart_format": True,
    }
    
    response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
    response = json.loads(response.to_json())
    transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
    return transcript


def model_claude(prompt, model="claude-3-5-sonnet-20240620"):
    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        temperature=0,
        system="you are an assistant",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    return message.content[0].text