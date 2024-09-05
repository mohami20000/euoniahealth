from flask import Flask, request, jsonify
from flask_cors import CORS
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import os
import asyncio
import logging
from dotenv import load_dotenv
from chat_model import LlmDummyMock

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

logging.basicConfig(level=logging.DEBUG)



@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    try:
        ai_response = user_message  # model_claude(user_message)
    except Exception as e:
        print(f"Error calling API: {str(e)}")
        ai_response = "I'm sorry, I'm having trouble processing your request right now."
    
    return jsonify({'response': ai_response}, {'attachment': ""})

@app.route('/api/transcribe', methods=['POST', 'OPTIONS'])
def transcribe():
    if request.method == 'OPTIONS':
        return ('', 204)

    logging.debug("Received request to /api/transcribe")
    if 'audio' not in request.files:
        logging.error("No audio file provided in request")
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    logging.debug(f"Received audio file: {audio_file.filename}")
    
    # Save the file temporarily
    temp_path = '/Users/mohami/Desktop/personalProjects/CBT_chatbot/chat_interface/tmp/audio_file.wav'
    audio_file.save(temp_path)
    
    try:
        transcript = 'transcript' # transcribe_audio(temp_path)
        return jsonify({'transcript': transcript})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)



@app.websocket("/llm-websocket/{call_id}")
async def websocket_handler(websocket: WebSocket, call_id: str):
    await websocket.accept()
    print(f"Handle llm ws for: {call_id}")
    
    llm_client = LlmDummyMock()

    # send first message to signal ready of server
    response_id = 0
    first_event = llm_client.draft_begin_message()
    await websocket.send_text(json.dumps(first_event))

    async def stream_response(request):
        nonlocal response_id
        for event in llm_client.draft_response(request):
            await websocket.send_text(json.dumps(event))
            if request['response_id'] < response_id:
                return # new response needed, abandon this one

    try:
        while True:
            message = await websocket.receive_text()
            request = json.loads(message)
            # print out transcript
            os.system('cls' if os.name == 'nt' else 'clear')
            # print(json.dumps(request, indent=4))
            
            if 'response_id' not in request:
                print('_'*50)
                continue # no response needed, process live transcript update if needed
            response_id = request['response_id']
            asyncio.create_task(stream_response(request))
    except WebSocketDisconnect:
        print(f"LLM WebSocket disconnected for {call_id}")
    except Exception as e:
        print(f'LLM WebSocket error for {call_id}: {e}')
    finally:
        print(f"LLM WebSocket connection closed for {call_id}")

@app.post("/api/create-web-call")
async def create_web_call():
    url = "https://api.retellai.com/v2/create-web-call"
    headers = {
        "Authorization": f"Bearer key_dee7d16f6712dce213eed111f45c",
        "Content-Type": "application/json"
    }
    payload = {
        "agent_id": "agent_b38905620a0c2466a1f09a20bb",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return {"access_token": data["access_token"]}
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)