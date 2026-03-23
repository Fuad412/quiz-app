import os
import json
from google import genai
from pydantic import BaseModel
from typing import List
from .models import Quiz, Question, Choice

class ChoiceModel(BaseModel):
    text: str
    is_correct: bool

class QuestionModel(BaseModel):
    text: str
    choices: List[ChoiceModel]

class QuizModel(BaseModel):
    title: str
    questions: List[QuestionModel]

def generate_quiz_from_topic(topic: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please get a free API key from aistudio.google.com and add it to your .env file.")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"Generate a multiple choice quiz about '{topic}'. It should have a catchy title and exactly 5 challenging but fair questions. Each question must have exactly 4 choices, with exactly one correct choice."

    # Force JSON format output using Structured Outputs (Type annotations)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': QuizModel,
        },
    )
    
    quiz_data_str = response.text
    quiz_data = json.loads(quiz_data_str)
    
    return quiz_data
