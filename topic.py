from bertopic import BERTopic
from sklearn.datasets import fetch_20newsgroups
import transcribe
import re


from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# Load the model and tokenizer
model_name = "google/flan-t5-base"  # or "google/flan-t5-large", "google/flan-t5-xl"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch.float32)

text = 'the current polical climate in the us is very divisive. many people are angry and frustrated with the government. there is a lot of misinformation and fake news circulating on social media. it is important to stay informed and to fact-check information before sharing it. we need to come together as a country and work towards common goals, rather than focusing on our differences.'
prompt = f"What is the main opinion of the following text:\n{text}"
inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
max_length=60
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

tr = transcribe.get_trancript_ytTapi("yKuwrnCfsFQ")
full_text = ' '.join([snippet.text for snippet in tr.snippets])
sentences = re.split(r'[.!?]+', full_text)

from bertopic.representation import KeyBERTInspired
representation_model = KeyBERTInspired()
topic_model = BERTopic(representation_model=representation_model)

topic_model = BERTopic(language="english", calculate_probabilities=True, verbose=True)
topics, probs = topic_model.fit_transform(sentences)

topic_model.get_topic_info()
topic_model.get_topic(0)
topic_model.get_topics()
topic_model.get_document_info(sentences)
topic_model.get_topic(topic=1)
text = topic_model.get_representative_docs()[0]
text = '.'.join([t for t in text])



 
docs = fetch_20newsgroups(subset='all',  remove=('headers', 'footers', 'quotes'))['data']

topics, probs = topic_model.fit_transform(docs)

pass


