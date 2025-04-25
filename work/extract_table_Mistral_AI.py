import sys

sys.path.append(r"C:\Users\lvolat\Documents\cocoAI")
from mistralai import Mistral
from common.keys import MISTRAL_API_KEY

api_key = MISTRAL_API_KEY
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model= model,
    messages = [
        {
            "role": "user",
            "content": "quelle est la météo courante à Paris?",
        },
    ]
)
print(chat_response.choices[0].message.content)