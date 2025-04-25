import sys

sys.path.append(r"C:\Users\lvolat\Documents\cocoAI")
from common.keys import HUGGINGFACE_API_KEY
from huggingface_hub import hf_hub_download
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
)

huggingface_model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

required_files = [
    "special_tokens_map.json",
    "generation_config.json",
    "tokenizer_config.json",
    "model.safetensors",
    "eval_results.json",
    "tokenizer.model",
    "tokenizer.json",
    "config.json",
]

#ne tourne pas car manque de RAM

for filename in required_files:
    download_location = hf_hub_download(
        repo_id=huggingface_model, filename=filename, token=HUGGINGFACE_API_KEY
    )
    print(f"File downloaded to {download_location}")

model = AutoModelForCausalLM.from_pretrained(huggingface_model)
tokenizer = AutoTokenizer.from_pretrained(huggingface_model)

# Create a pipeline
chat = pipeline("text-generation", model=model, tokenizer=tokenizer, maxlength=1000)

response = chat("Hello, how are you?")
print(response)
