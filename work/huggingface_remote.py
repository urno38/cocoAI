# API endpoint and token
import base64
import sys

sys.path.append(r"C:\Users\lvolat\Documents\cocoAI")
import json
import requests
from common.keys import HUGGINGFACE_API_KEY
from common.path import WORK_PATH


url = "https://api-inference.huggingface.co/models/microsoft/trocr-large-handwritten"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

image_path = WORK_PATH / "capture.png"

# The question to ask
question = "What script is in the image?"

# Path to the output file
output_path = "output.json"

# Read the image file
with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Prepare the payload
payload = {"inputs": {"image": image_data, "question": question}}

# Send the request
response = requests.post(url, headers=headers, json=payload)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    output = response.json()

    # Write the output to a file
    with open(output_path, "w") as f:
        json.dump(output, f, indent=4)

    print(f"Output written to {output_path}")
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)
