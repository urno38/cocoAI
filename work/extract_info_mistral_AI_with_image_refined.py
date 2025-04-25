import base64
import json
from pathlib import Path
import sys

import pandas as pd


sys.path.append(r"C:\Users\lvolat\Documents\cocoAI")
from common.path import DATA_PATH, WORK_PATH
from mistralai import Mistral
from common.keys import MISTRAL_API_KEY


def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None


# Path to your image
image_path = DATA_PATH / "capture_moins_claire_avec_tableau.png"

# Getting the base64 string
base64_image = encode_image(image_path)

# Retrieve the API key from environment variables
api_key = MISTRAL_API_KEY

# Specify model
model = "pixtral-12b-2409"

# Initialize the Mistral client
client = Mistral(api_key=api_key)

# Define the messages for the chat
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "trouve les immobilisations de l'année 2015 dans ce document",
            },
            {
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{base64_image}",
            },
        ],
    }
]

# Get the chat response
chat_response = client.chat.complete(
    model=model,
    messages=messages,
)

# Print the content of the response
json_str = chat_response.choices[0].message.content
print(json_str)
if isinstance(json_str,str):
    output_path = Path("str_output.txt")
    with open(output_path,'w',encoding='utf-8') as f:
        f.write(json_str)
    print('output written in',output_path.resolve())
else:
    json_list = json.loads(json_str)
    # Convert the dictionary to a Pandas DataFrame
    df = pd.json_normalize(json_list)
    df.to_csv("output.csv")
    # Print the DataFrame
    print(df)
