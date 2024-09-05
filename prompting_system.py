import anthropic
import os
from dotenv import load_dotenv
import prompts

load_dotenv()

anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def make_styler_prompt(transcript, conversation):
    styler_prompt = f"""You are an AI assistant trained in analyzing and emulating therapy conversation styles. Your task is to rewrite the last message from the AI therapist "eunoia" in a style that closely matches the provided transcript of a human therapist's session.
Here are your instructions:

1. Carefully analyze the speaking style, tone, and language patterns used by the therapist in the provided transcript.

2. Pay attention to:
- Sentence structure and length
- Use of therapeutic language and techniques
- Level of formality or casualness
- Use of empathy and rapport-building language
- Any unique phrases or mannerisms

3. Rewrite eunoia's last response to mimic this style as closely as possible while maintaining the original content and intent of eunoia's message.

Here is the transcript to base the style on:
{transcript}
"""
    return styler_prompt

def get_model_response(full_prompt, system_prompt):
    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
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

def main():
    transcript = """"""
    conversation = """First Session:
user: hi
eunoia: Hello there! Welcome to our session. I'm Eunoia, and I'm here to support you. How are you feeling today as we begin our conversation?
"""
    temp_prompt = """Here is the conversation with Eunoia, ending with the message you should rewrite:
{conversation}
Please rewrite Eunoia's last response in the style of the provided transcript. Respond only with the rewritten message, nothing else.
eunoia's rewritten last message:"""

    prompt = make_styler_prompt(transcript, conversation=conversation)
    print(prompt)
    print('_'*50)
    ai_response = get_model_response(temp_prompt, system_prompt=prompt)
    print(f"eunoia: {ai_response}")
    # while True:
    #     user_input = input("User: ")
    #     if user_input.lower() == 'quit':
    #         break
    #     ai_response = get_model_response(prompt)
    #     print(f"eunoia: {ai_response}")

if __name__ == "__main__":
    main()
    

# eunoia: I'm glad you're here for our first session. Can we start by setting an agenda for today? What would be most helpful for us to focus on?
# user: i daydream too much and it wastes my time
# eunoia: Thank you for bringing that up. Daydreaming is certainly something we can work on together. Before we dive in, I'd like to set a clear agenda for our session today. It sounds like addressing your daydreaming is a priority. Is there anything else you'd like us to focus on?
# user: no
# eunoia: Okay, so we'll focus on your daydreaming and how it's affecting your time. Can you tell me more about this? When do you find yourself daydreaming most often? And how much time do you think it's taking up in your day?
# user: I noticed they occur when certain trigger happen. for example, if i watch a game of thrones episode, i will keep daydreaming about this fictional character i created in game of thrones. the dreams are usually me dreaming i am some character i created that is smart, successful and very rich
# eunoia: I see. So these daydreams often start after watching something like Game of Thrones, and you imagine yourself as a character who's very successful. That's interesting. Can you tell me, how do you feel when you're having these daydreams? And I'm curious, what do you think might be behind creating this particular kind of character in your mind?
# user: They are genuinely very fun. that is why i do them. I think they resemble my goals a little bit. to be powerful, rich, smart, good looking, and things like that
# eunoia: I appreciate you sharing that. It's understandable these daydreams are enjoyable and reflect some of your goals. You mentioned they're taking up too much time, though. Could you estimate how many hours a day you spend daydreaming? And in what ways do you feel it's interfering with your daily life?
# user: at least one hour per day. I am very ambitious and to achieve my goals, i need to work very hard. when i daydream, i just dream and do nothing so it prevents me from working towards my goals. last time, i wanted to do work but i got dragged in this daydream and i put off work
# eunoia: I appreciate you sharing that information. It's helpful to understand how these daydreams are affecting your daily life. You mentioned they take up at least an hour a day and sometimes prevent you from working towards your goals. That sounds frustrating. I'm wondering, have you noticed any patterns in when these daydreams tend to occur? For example, are they more likely to happen at certain times of day or in specific situations? And when you find yourself daydreaming instead of working, what thoughts go through your mind?
# user: it is not specific to time of day i think. i think its more related to when a trigger happens. I usually think about how i am putting off work and i just tell myself that next time i will not do this and i will work instead.
# eunoia: Thank you for sharing that information. It's good to know these daydreams are more trigger-related than time-specific. You mentioned watching Game of Thrones can be a trigger. Are there other triggers you've noticed?
# user: I think when i see someone i feel competitive with getting achievements, i will daydream about beating him and things like that. or if i see someone living the life i want, i will also daydream. Any movie or show that can create fictional character in will also make me daydream.
# eunoia: Thank you for providing those additional details. It seems like your daydreams are often triggered by external stimuli that relate to your goals or desires. This is valuable information for us to work with.
# Given what you've shared, I'd like to suggest a couple of strategies we could explore:

# Awareness and Logging: Start keeping a simple log of when you daydream, what triggered it, and how long it lasted. This can help us identify patterns and triggers more precisely.
# Grounding Techniques: We could work on some quick grounding exercises to help you snap back to reality when you notice you're daydreaming.

# Which of these do you think might be most helpful to start with? Or is there another approach you'd prefer?
