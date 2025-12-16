import os
import re
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def check_timestamp(text):
    """Check if string starts with [HH:MM:SS]"""
    pattern = r'^\[\d{2}:\d{2}:\d{2}\].*'
    return re.match(pattern, text)

#read summeries into dataframe
def read_summaries_to_df(dir):
    import pandas as pd

    files = [file for file in os.listdir(dir) if file.endswith('.txt')]
    files.sort()
    data = []
    for file in files:
        if file == 'all_summaries.txt':
            continue
        file_path = os.path.join(dir, file)
        
        video_id = file.split('.')[0]
        with open(file_path, 'r') as file:
            lines = file.readlines()
        for line in lines:
            timestamp_pattern = r'^\[\d{2}:\d{2}:\d{2}\]'
            timestamp_match = re.match(timestamp_pattern, line)
            if not bool(timestamp_match):
                continue
            ts_start, ts_end = timestamp_match.span()
            text = line[ts_end:].strip()
            embeddings = model.encode(text)
            data.append({'video_id': video_id, 'ts':line[ts_start: ts_end], 'text': line[ts_end:].strip(), 'embeddings': embeddings})
    df = pd.DataFrame(data)
    return df

df = read_summaries_to_df("summary")

clustering = DBSCAN(eps=0.5, min_samples=2, metric='cosine')
clusters = clustering.fit_predict(df['embeddings'].values.tolist())
args = np.argwhere(clusters == 2)
cluster_df = df['text'].iloc[args.flatten().tolist()]


for idx in len(cluster_df):
    print(cluster_df.iloc[idx])

pass