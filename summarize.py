import torch
from transformers import pipeline
from pathlib import Path
import sys

#read transcript
path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\lahir\code\otherside\transcript.txt")
if not path.exists():
    raise FileNotFoundError(f"Transcript file not found: {path}")
with path.open("r", encoding="utf-8") as f:
    transcript = f.read()

# Load summarizer (smallest, efficient)
summarizer = pipeline("summarization", model="google/flan-t5-small", device=-1)

def chunk_text(text, max_tokens=800):
    words = text.split()
    for i in range(0, len(words), max_tokens):
        yield " ".join(words[i:i+max_tokens])

def summarize_transcript(transcript):
    chunk_summaries = []
    tokens = len(transcript.split())
    n = 0
    for chunk in chunk_text(transcript):
        print(f"Summarizing chunk {n+1} / {(tokens // 800) + 1}",end='\r')
        n += 1
        # if n==10:
        #     break
        summary = summarizer("summarize: " + chunk, max_length=100, min_length=20, do_sample=False)[0]['summary_text']
        chunk_summaries.append(summary)
    # combined = " ".join(chunk_summaries)
    # final_summary = summarizer("summarize: " + combined, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
    return chunk_summaries

summary = summarize_transcript(transcript)

words = transcript.split()
" ".join(words[0:800])
pass