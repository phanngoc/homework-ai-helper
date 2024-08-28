import openai
import cv2
import os
import numpy as np
import base64
from pydantic import BaseModel
import openai

class Step(BaseModel):
    explanation: str
    output: str

class MathResponse(BaseModel):
    steps: list[Step]
    final_answer: str

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def resolve_solution(url, action):
    if action == 'suggestion':
        question_text = "Hướng dẫn người dùng từng bước giải quyết"
    else:
        question_text = "Chọn đáp án đúng và đưa ra lời giải thích"

    image_base64 = encode_image(url)
    system_message = "Bạn là một gia sư toán hữu ích"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": question_text,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    },
                },
            ]
            },
        ],
        max_tokens=300,
        response_format=MathResponse,
    )
    return response.choices[0].message.content