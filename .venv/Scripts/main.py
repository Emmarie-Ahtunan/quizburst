from fastapi import FastAPI
from pydantic import BaseModel

import motor.motor_asyncio
import openai
import os
from dotenv import load_dotenv

app = FastAPI()


# Set up MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
db = client['quizburst']
questions_collection = db['questions']
scores_collection = db['scores']


# Set up OpenAI API credentials
openai.api_key = ''
load_dotenv()
openai.api_key = os.getenv("open_api_key")

# Function to generate quiz questions using OpenAI

async def generate_quiz_questions(topic, num_questions):
    prompt = f"Generate {num_questions} quiz questions on the topic of {topic}."
    
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=100,
        n=num_questions,
        stop=None,
        temperature=0.7
    )
    
    questions = [choice['text'] for choice in response.choices]
    return questions

# Function to fetch quiz questions from MongoDB
@app.get('/dashboard/play-quiz')
async def get_quiz_questions(topic, limit : int):
    questions = []
    async for question in questions_collection.find({"topic": topic}).limit(limit):
        questions.append(question)
    return questions

# Function to insert a new quiz question into MongoDB
@app.post('/dashboard/play_quiz')
async def insert_quiz_question(question_data):
    result = await questions_collection.insert_one(question_data)
    return result.inserted_id

# Function to store user quiz score in MongoDB
@app.put('/dashboard/play_quiz')
async def store_quiz_score(user_id, quiz_id, score):
    score_data = {
        'user_id': user_id,
        'quiz_id': quiz_id,
        'score': score
    }
    result = await scores_collection.insert_one(score_data)
    return result.inserted_id

# Example usage
async def main():
    # Generate quiz questions using OpenAI
    topic = 'History'
    num_questions = 5
    quiz_questions = await generate_quiz_questions(topic, num_questions)
    print(quiz_questions)

    # Fetch quiz questions from MongoDB
    topic = 'Geography'
    limit = 10
    questions = await get_quiz_questions(topic, limit)
    print(questions)
# Insert a new quiz question into MongoDB
    new_question = {
        'topic': 'Science',
        'question': 'What is the boiling point of water?',
        'options': ['100°C', '0°C', '50°C', '200°C'],
        'answer': '100°C'
    }
    new_question_id = await insert_quiz_question(new_question)
    print(f"New question inserted with ID: {new_question_id}")

    # Store user quiz score in MongoDB
    user_id = '123456'
    quiz_id = '7890'
    score = 80
    score_id = await store_quiz_score(user_id, quiz_id, score)
    print(f"User quiz score stored with ID: {score_id}")

# Run the event loop
if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
