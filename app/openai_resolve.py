import re
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
  print('encode_image:image_path', image_path)
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def resolve_solution(url, action):
    if action == 'suggestion':
        question_text = "Hướng dẫn người dùng từng bước giải quyết"
    else:
        question_text = "Chọn đáp án đúng và đưa ra lời giải thích"

    image_base64 = encode_image(url)
    system_message = "Bạn là một gia sư toán hữu ích"
    
    dummy_response = {
        "response": {
            "content": "{\"steps\":[{\"explanation\":\"Sử dụng quy tắc trừ của logarithm: ln(a) - ln(b) = ln(a/b).\",\"output\":\"ln(7a) - ln(3a) = ln(\\\\frac{7a}{3a})\"},{\"explanation\":\"Rút gọn biểu thức: \\\\frac{7a}{3a} = \\\\frac{7}{3}, nên: ln(\\\\frac{7a}{3a}) = ln(\\\\frac{7}{3}).\",\"output\":\"ln(\\\\frac{7}{3})\"},{\"explanation\":\"Ta thấy ln(\\\\frac{7}{3}) tương đương với đáp án C.\",\"output\":\"Vậy, đáp án đúng là C: ln(\\\\frac{7}{3}).\"}],\"final_answer\":\"C: ln(\\\\frac{7}{3})\"}",
            "parsed": {
                "final_answer": "C: ln(\\frac{7}{3})",
                "steps": [
                    {
                        "explanation": "Sử dụng quy tắc trừ của logarithm: ln(a) - ln(b) = ln(a/b).",
                        "output": "ln(7a) - ln(3a) = ln(\\frac{7a}{3a})"
                    },
                    {
                        "explanation": "Rút gọn biểu thức: \\frac{7a}{3a} = \\frac{7}{3}, nên: ln(\\frac{7a}{3a}) = ln(\\frac{7}{3}).",
                        "output": "ln(\\frac{7}{3})"
                    },
                    {
                        "explanation": "Ta thấy ln(\\frac{7}{3}) tương đương với đáp án C.",
                        "output": "Vậy, đáp án đúng là C: ln(\\frac{7}{3})."
                    }
                ]
            },
            "refusal": None,
            "role": "assistant",
            "tool_calls": []
        }
    }

    return dummy_response

    response = client.beta.chat.completions.parse(
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
    math_response = response.choices[0].message
    if math_response.parsed:
        return math_response.to_dict()
    elif math_response.refusal:
        return math_response.to_dict()