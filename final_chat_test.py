import anthropic
import sounddevice as sd
from scipy.io import wavfile
import numpy as np
import threading
import queue
import os
from datetime import datetime
import json
from dotenv import load_dotenv
import final_prompts
import speech_recognition as sr
import pyaudio
import wave
import asyncio
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

load_dotenv()


DEEPGRAM_API_KEY="d082a381b6fc9fbeb2ec2245398296e13c99105c"
deepgram = DeepgramClient(DEEPGRAM_API_KEY)


anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def get_model_response(full_prompt, system_prompt):
    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=300,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": full_prompt
                    }
                ]
            }
        ]
    )
    
    return message.content[0].text

def record_audio(filename, fs=44100, channels=1):
    print("Recording... Press Enter to stop.")
    recording = []
    stop_event = threading.Event()

    def callback(indata, frames, time, status):
        if status:
            print(status)
        recording.append(indata.copy())

    def wait_for_enter():
        input()
        stop_event.set()

    with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
        threading.Thread(target=wait_for_enter, daemon=True).start()
        stop_event.wait()

    recording = np.concatenate(recording, axis=0)
    recording = np.int16(recording * 32767)

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(recording.tobytes())

    print("Recording finished and saved.")

async def transcribe_audio(audio_file):
    with open(audio_file, "rb") as file:
        buffer_data = file.read()

    payload: FileSource = {
        "buffer": buffer_data,
    }
    options = PrerecordedOptions(
        model="nova-2",
        smart_format=True,
    )
    
    response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
    response = json.loads(response.to_json())
    transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
    return transcript

async def main():
    conversation = """"""
    while True:
        record_audio('temp.wav')
        user_input = await transcribe_audio('temp.wav')
        # user_input = input("Mo: ")
        print("Mo: ", user_input)
        if user_input.strip().lower() == 'quit.':
            break
        conversation += f"\nMo: {user_input}"
        ai_response = get_model_response(conversation, system_prompt=final_prompts.FIRST_SESSION_PROMPT)
        print(f"eunoia: {ai_response}")
        conversation += f"\neunoia: {ai_response}"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/Users/mohami/Desktop/personalProjects/CBT_chatbot/chat_interface/conversation_{timestamp}.txt"
    with open(filename, "w") as file:
        file.write(conversation)
    print(f"Conversation saved to {filename}")

if __name__ == "__main__":
    asyncio.run(main())