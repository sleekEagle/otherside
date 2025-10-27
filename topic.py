from bertopic import BERTopic
from sklearn.datasets import fetch_20newsgroups
import transcribe
import re
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch


tr = transcribe.get_trancript_ytTapi("-9LFj6YOK2U")
full_text = ' '.join([snippet.text for snippet in tr.snippets])
sentences = re.split(r'[.!?]+', full_text)

from bertopic.representation import KeyBERTInspired
representation_model = KeyBERTInspired()
topic_model = BERTopic(representation_model=representation_model)
topic_model = BERTopic(language="english", calculate_probabilities=True, verbose=True)

topic_model = BERTopic()
topics, probs = topic_model.fit_transform(sentences)

topic_model.get_topic_info()
topic_model.get_topic(0)
topic_model.get_topics()
topic_model.get_document_info(sentences)
topic_model.get_topic(topic=2)
text = topic_model.get_representative_docs()[2]
text = '.'.join([t for t in text])

docs = fetch_20newsgroups(subset='all',  remove=('headers', 'footers', 'quotes'))['data']

topics, probs = topic_model.fit_transform(docs)

pass


