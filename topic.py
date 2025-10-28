from bertopic import BERTopic
from sklearn.datasets import fetch_20newsgroups
import transcribe
import re
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import OpenAI, MaximalMarginalRelevance
from bertopic.representation import TextGeneration
from bertopic.representation import KeyBERTInspired
from pytube import YouTube
from typing import List, Tuple
from sklearn.feature_extraction.text import CountVectorizer

class TopicAnalyzer:
    def __init__(self):
        self.topic_model = BERTopic(
            embedding_model="all-MiniLM-L6-v2",
            vectorizer_model=CountVectorizer(stop_words="english", ngram_range=(1, 2)),
            calculate_probabilities=True,
            verbose=True
        )
    
    def get_sentences(self, yt_id):
        tr = transcribe.get_trancript_ytTapi(yt_id)
        full_text = ' '.join([snippet.text for snippet in tr.snippets])
        sentences = re.split(r'[.!?]+', full_text)
        return sentences
    
    def get_topics(self, yt_id):
        sentences = self.get_sentences(yt_id)
        topics, probabilities = self.topic_model.fit_transform(sentences)
        topic_sections = {}
        for sentence, topic in zip(sentences, topics):
            if topic not in topic_sections:
                topic_sections[topic] = []
            topic_sections[topic].append(sentence)
        return topic_sections, topics, probabilities


links = [r'https://www.youtube.com/watch?v=wiuRDSQLjV0',
r'https://www.youtube.com/watch?v=8enXRDlWguU',
r'https://www.youtube.com/watch?v=K5NP2wf0LLk',
r'https://www.youtube.com/watch?v=fpbA0BSR5gM',
r'https://www.youtube.com/watch?v=JMObz0Dgq7M']

ta = TopicAnalyzer()

for link in links:
    yt_id = link.split('v=')[1]
    topic_sections, topics, probabilities = ta.get_topics(yt_id)
ta.topic_model.get_topic(3)
topic_sections[2]
ta.topic_model.get_topic_info()
pass




