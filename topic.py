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


# from sklearn.datasets import fetch_20newsgroups
# docs = fetch_20newsgroups(subset='all',  remove=('headers', 'footers', 'quotes'))['data']

# topic_model = BERTopic(language="english", calculate_probabilities=True, verbose=True)
# topics, probs = topic_model.fit_transform(docs)
# freq = topic_model.get_topic_info()
# topic_model.get_topic(0)
# topic_model.topics_[:10]
# topic_model.visualize_topics()
# topic_model.visualize_distribution(probs[200], min_probability=0.015)


tr = transcribe.get_trancript_ytTapi("-9LFj6YOK2U")
full_text = ' '.join([snippet.text for snippet in tr.snippets])
sentences = re.split(r'[.!?]+', full_text)

topic_model = BERTopic(
    embedding_model="all-MiniLM-L6-v2",
    vectorizer_model=CountVectorizer(stop_words="english", ngram_range=(1, 2)),
    calculate_probabilities=True,
    verbose=True
)
topics, probabilities = topic_model.fit_transform(sentences)
topic_info = topic_model.get_topic_info()

topic_sections = {}
for sentence, topic in zip(sentences, topics):
    if topic not in topic_sections:
        topic_sections[topic] = []
    topic_sections[topic].append(sentence)

topic_sections[6]
topic_model.get_topic(6)



# 2. SOTA Embedding Model
embedder = SentenceTransformer("intfloat/e5-small-v2")
# 3. Dimensionality reduction (UMAP)
umap_model = UMAP(
    n_neighbors=15,
    n_components=5,
    min_dist=0.0,
    metric='cosine',
    random_state=42
)
# 4. Clustering (HDBSCAN)
hdbscan_model = HDBSCAN(
    min_cluster_size=15,      # tweak based on podcast length
    metric='euclidean',
    cluster_selection_method='eom',
    prediction_data=True
)
# 5. Vectorizer (c-TF-IDF)
ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
# 6. LLM for topic labeling (zero-shot)
representation_model = KeyBERTInspired()
# Optional: Add MMR for diverse representative docs
mmr = MaximalMarginalRelevance(diversity=0.3)
# 7. Build BERTopic with all SOTA components
topic_model = BERTopic(
    embedding_model=embedder,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    vectorizer_model=ctfidf_model,
    representation_model=representation_model,
    min_topic_size=10,
    verbose=True
)
topics, probs = topic_model.fit_transform(docs)


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


