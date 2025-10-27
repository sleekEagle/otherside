from sklearn.datasets import fetch_20newsgroups
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# Load the model and tokenizer
model_name = "google/flan-t5-base"  # or "google/flan-t5-large", "google/flan-t5-xl"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch.float32)

text = 'And you can buy a car like that in China for three or $4,000 So, not not uh so there \'s the I think you can buy a Chevy Spark, which is actually not an electric car. Like like the most American car you can buy, I think right now >> it \'s either a Nissan or a Toyota outside of Tesla'
prompt = f"Summerize: \n{text}"
inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
max_length=20
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_length=max_length,
        min_length=30,
        length_penalty=20.0,
        num_beams=4,
        early_stopping=True
    )
summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

