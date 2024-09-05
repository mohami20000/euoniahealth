import anthropic
import sounddevice as sd
from scipy.io import wavfile
import numpy as np
import threading
import queue
import os
from datetime import datetime
import final_prompts

anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

beginSentence = "Hello Mo, I'm Eunoia. It's nice to meet you. Welcome to our first session. How are you feeling about being here today?"

class LlmDummyMock:
    def __init__(self):
        
        self.begin_sentence = "How may I help you?"
    
    def draft_begin_message(self):
        return {
            "response_id": 0,
            "content": beginSentence,
            "content_complete": True,
            "end_call": False,
        }
    
    def convert_transcript_to_model_messages(self, transcript):
        messages = []
        for utterance in transcript:
            if utterance["role"] == "agent":
                messages.append({
                    "role": "assistant",
                    "content": utterance['content']
                })
            else:
                messages.append({
                    "role": "user",
                    "content": utterance['content']
                })
        return messages
    
    def combine_same_role_messages(self, prompt):
        if not prompt:
            return prompt

        combined_prompt = [prompt[0]]

        for current_message in prompt[1:]:
            if current_message['role'] == combined_prompt[-1]['role']:
                # If the current message has the same role as the last message in the combined list,
                # append its content to the last message
                combined_prompt[-1]['content'] += "\n\n" + current_message['content']
            else:
                # If the roles are different, add the current message as a new entry
                combined_prompt.append(current_message)

        return combined_prompt
    
    def prepare_prompt(self, request):
        transcript_messages = self.convert_transcript_to_model_messages(request['transcript'])
        if not transcript_messages or transcript_messages[0]['role'] != 'user':
            prompt = [{"role": "user", "content": "Hello"}]
        else:
            prompt = []
        for message in transcript_messages:
            prompt.append(message)

        if request['interaction_type'] == "reminder_required":
            prompt.append({
                "role": "user",
                "content": "(Now the user has not responded in a while, you would say:)",
            })
        combined_prompt = self.combine_same_role_messages(prompt)

        return combined_prompt

    def draft_response(self, request):
        print('*'*50)      
        prompt = self.prepare_prompt(request)
        with anthropic_client.messages.stream(
            max_tokens=300,
            system=final_prompts.EVALUATION_SESSION_PROMPT,
            messages=prompt,
            temperature=0,
            model="claude-3-5-sonnet-20240620",
        ) as stream:
            for chunk in stream.text_stream:
                print(chunk)
                if chunk is not None:
                    yield {
                        "response_id": request['response_id'],
                        "content": chunk,
                        "content_complete": False,
                        "end_call": False,
                    }
        
        yield {
            "response_id": request['response_id'],
            "content": "",
            "content_complete": True,
            "end_call": False,
        }