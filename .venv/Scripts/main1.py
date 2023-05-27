from fastapi import FastAPI
import motor.motor_asyncio
import openai
import os
#from dotenv import load_dotenv
from pydantic import BaseModel

class quiz(BaseModel):
    id:int
    topic:str
    question:str
    ans: str=""
    done:bool

app=FastAPI()
que=[]
OPENAI_API_KEY="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"
#load_dotenv()
openai.api_key =OPENAI_API_KEY

@app.get("/que/")
async def read_questions():
     return que

@app.post("/que/")
async def create_question(request: quiz):
     request.ans = await askque_from_openai(request)
     que.append(request)
     return {"id": len(que),"ans": request.ans}

@app.put("/que/{request_id}")
async def update_question(request_id: int, request: quiz):
     que[request_id - 1] = request
     return {"success": True}

@app.delete("/que/{request_id}")
async def delete_question(request_id: int):
     que.pop(request_id - 1)
     return {"success": True}

async def askque_from_openai(request: quiz):
    prompt = f"Write advice on how to achieve the task titled '{request.topic}' with question '{request.question}'",
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.3,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    text_advice = response.choices[0]["text"]
    return text_advice