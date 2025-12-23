from llama_cpp import Llama
import transcribe
import os
import re
import platform
from openai import OpenAI
import requests
import difflib

def count_tokens(text):
    resp = requests.post(
        "http://localhost:8080/tokenize",
        json={"content": text}
    )
    return len(resp.json()["tokens"])

def clean_sentence(sentence):
    # Remove bullet points (•, -, *, etc.)
    sentence = re.sub(r'^[•\-*\d+\.\)]\s*', '', sentence)
    
    # Remove (starts at [timestamp]) patterns
    sentence = re.sub(r'\s*\(starts at\s*\[.*?\]\)\s*$', '', sentence)
    
    # Alternative if timestamps vary:
    # sentence = re.sub(r'\s*\(.*?starts? at.*?\[.*?\].*?\)\s*$', '', sentence)
    
    # Remove any remaining parentheses with timestamps
    sentence = re.sub(r'\s*\(\s*[\d:]+.*?\s*\)\s*$', '', sentence)
    
    # Clean up extra whitespace
    sentence = ' '.join(sentence.split())
    
    return sentence

def string_similarity(str1, str2):
    """Returns similarity ratio between 0 and 1"""
    return difflib.SequenceMatcher(None, str1, str2).ratio()

def split_transcript_by_time(transcript_text, chunk_minutes=10):
    """
    Split transcript into chunks based on timestamps.
    Each chunk contains approximately X minutes of content.
    """
    # Parse timestamp lines
    lines = transcript_text.strip().split('\n')
    chunks = []
    current_chunk = []
    current_time = 0
    
    timestamp_pattern = r'\[(\d{2}):(\d{2}):(\d{2})\]'
    
    for line in lines:
        # Check if line has timestamp
        match = re.search(timestamp_pattern, line)
        if match:
            hours, minutes, seconds = map(int, match.groups())
            total_minutes = hours * 60 + minutes + seconds / 60
            
            # Start new chunk every X minutes
            if total_minutes - current_time >= chunk_minutes and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_time = total_minutes
            
            current_chunk.append(line)
        else:
            if current_chunk:  # Continue current chunk
                current_chunk.append(line)
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks


class UseLlama:
    def __init__(self):
        self.server_url="http://localhost:8080"
    
    def request(self, sys_rols, prompt, max_tokens):
        resp = self.client.chat.completions.create(
            model="local-model",   # name is ignored by llama.cpp
            messages=[
                {"role": "system", "content": sys_rols},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content
    
    def summarize_chunk(self, chunk_text, chunk_num):
        prompt = f"""Summarize this YouTube transcript chunk {chunk_num} into clear, concise bullet points.

        Transcript:
        {chunk_text}

        INSTRUCTIONS:
        1. **EXCLUDE**: Promotional content, ads, sponsor messages, calls to action ("like and subscribe"), and channel promotions
        2. **EXCLUDE**: Self-referential content about the video itself ("in this video", "today we'll be talking about")
        3. **EXCLUDE**: Repetitive filler phrases and conversational fluff
        4. **INCLUDE**: Only substantive information, key ideas, important facts, examples, data, and meaningful content
        5. Format each point as a bullet with timestamp
        6. Focus on educational/informative content that has value to a viewer

        CONTENT FILTERING RULES:
        - SKIP if it contains: "like and subscribe", "hit the bell icon", "sponsor", "patreon", "merch", "check out my"
        - SKIP if it contains: "in this video", "today we're going to", "welcome back to the channel"
        - SKIP if it's purely promotional or calls to action
        - INCLUDE only if it provides actual information, analysis, or educational content

        EXAMPLE FILTERING:
        ❌ EXCLUDE: "Before we begin, don't forget to like and subscribe!" (promotional)
        ❌ EXCLUDE: "This video is brought to you by NordVPN..." (advertisement)
        ❌ EXCLUDE: "So today in this video I want to talk about..." (self-referential)
        ✅ INCLUDE: "The study showed a 45% increase in efficiency with the new method." (substantive)
        ✅ INCLUDE: "Quantum computing uses qubits that can exist in multiple states simultaneously." (educational)

        EXAMPLE FORMAT:
        • Main point or key idea from the transcript (starts at [timestamp])
        • Another important point discussed in this section (starts at [timestamp])
        • Significant example or case mentioned by the speaker (starts at [timestamp])

        # IMPORTANT:
        # - Create as many topics as naturally emerge from the content
        # - Topic summaries should be specific enough to be useful for navigation
        # - Each timestamp should mark when THAT SPECIFIC POINT begins
        # - Use "starts at [timestamp]" format for clarity
        # - Points should be distinct, not overlapping in content
        # - Include as many relevant points as possible from this segment

        Now create a bullet-point summary of the transcript:"""

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You analyze chunks of YouTube transcripts and create summaries with sections and timestamps"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.4,
            "max_tokens": 1000,
            "top_p": 0.9,
            "stream": False
        }
        response = requests.post(
            f"{self.server_url}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
        
    def non_overlapping_topics(self, topics):
        prompt = f"""You are given many sentenses with possibly overlapping meaning.
        Merge them into a final set of canonical sentenses.
        Do not invent new concepts.
        Return only the original sentenses and their corresponding final canonical sentense.
        sentenses:
        {topics}

        Output format:
        <Original sentense 1> : <New sentense 4>
        <Original sentense 2> : <New sentense 6>
        <Original sentense 3> : <New sentense 1>
        """

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You create sentenses with non overlapping meaning from possibly overlapping list of sentenses"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.4,
            "max_tokens": 1000,
            "top_p": 0.9,
            "stream": False
        }
        response = requests.post(
            f"{self.server_url}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
        
    def assign_topics(self, points, topics):
        prompt = f"""Assign each bullet point to exactly ONE of the following topics.
            Use ONLY the provided topics.
            Do NOT modify bullet point text and its timestamp.
            Do NOT omit any bullet.

            Topics:
            {topics}

            Bullet points:
            {points}

            Output format:
            - <bullet point 1> <topic 4>
            - <bullet point 2> <topic 6>
            - <bullet point 3> <topic 1>
            """

        payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a precise classifier."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 512,
                "top_p": 0.9,
                "stream": False
            }
        response = requests.post(
            f"{self.server_url}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

        
                
    def create_final_summary(self, chunk_summaries):
        # Combine all chunk summaries
        combined = "\n\n".join(chunk_summaries)
        
        prompt = f"""Organize these discussion points into logical topics:

        {combined}

        **TASK:**
        1. Group points into several logical topics
        2. Create a descriptive topic title for each group (ending with colon)
        3. Keep points under each topic in chronological order
        4. Maintain the exact text and timestamps of each point

        **REQUIRED OUTPUT FORMAT:**
        [Topic 1 description]:
        [Point 1] (timestamp)
        [Point 2] (timestamp)

        [Topic 2 description]:
        [Point 1] (timestamp)
        [Point 2] (timestamp)
        [Point 3] (timestamp)

        **RULES:**
        - One blank line between topics
        - Keep original timestamps
        - Each point on its own line

        Now organize the points:"""
            
        # messages = [
        #         {"role": "system", "content": "You organize points into logical topics with timestamps."},
        #         {"role": "user", "content": prompt}
        #     ]
            
        # response = self.llm.create_chat_completion(
        #         messages=messages,
        #         temperature=0.1,  # Low temperature for consistent formatting
        #         max_tokens=8000
        #     )
            
        # return response["choices"][0]["message"]["content"]

        ret = self.request("You organize points into logical topics with timestamps.", prompt, 16000)
        return ret
    
    def summarize_large_transcript(self, transcript_text):
        # Split into manageable chunks (e.g., 10-minute segments)
        chunks = split_transcript_by_time(transcript_text, chunk_minutes=10)
        
        summaries = []
        
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i+1}/{len(chunks)}...")
            
            # Summarize each chunk
            chunk_summary = self.summarize_chunk(chunk, chunk_num=i+1)
            summaries.append(chunk_summary)

        combined = "\n\n".join(summaries)
        comb_list = [clean_sentence(line) for line in combined.split('\n')]

        from bertopic import BERTopic
        from sklearn.datasets import fetch_20newsgroups

        topic_model = BERTopic(embedding_model="all-mpnet-base-v2")
        topics, probs = topic_model.fit_transform(comb_list)

        # #extract bullet points

        # point_list = []
        # topic_list = []
        # tmp_list = []
        # tmp_topic = ""
        # for i,l in enumerate(comb_list):
        #     if l.startswith('#'):
        #         if len(tmp_list)>0:
        #             point_list.append(tmp_list)
        #             tmp_list = []
        #             topic_list.append(tmp_topic)
        #         tmp_topic = l.partition("#")[2].partition("#")[2].strip()
        #     else:
        #         tmp_list.append(l)
        # topic_list.append(tmp_topic)
        # point_list.append(tmp_list)


        # topics = self.non_overlapping_topics('\n'.join(topic_list))
        # original_topics = [t.split(':')[0].strip() for t in topics.split('\n')]
        # new_topics = [t.split(':')[1].strip() for t in topics.split('\n')]

        # #replace old topics with new topics
        # mapped_topics = []
        # for t in topic_list:
        #     l = [string_similarity(t, ot) for ot in original_topics]
        #     idx = l.index(max(l))
        #     mapped_topics.append(new_topics[idx])

        # unique_t = list(set(mapped_topics))
        # summary = []
        # for i,t in enumerate(unique_t):
        #     idxs = [j for j, init_t in enumerate(mapped_topics) if init_t == t]
        #     #concat points
        #     p = [x for i in idxs for x in point_list[i] if len(x)>10]
        #     tmp = {}
        #     tmp['topic'] = t
        #     tmp['points'] = p
        #     summary.append(tmp)

        # pass




        # string_similarity
            
        # points = [line for line in comb_list if not line.startswith('#') and len(line)>10]
        # topics = [line.partition('[')[2].partition(']')[0].partition(':')[2] for line in comb_list if line.startswith('#')]
        # len(points)

        # topic_idx = [i for i, l in enumerate(comb_list) if l.startswith('#')]
        # seg = {}
        # for i in range(len(topic_idx)-1):
        #     p = comb_list[i+1 : topic_idx[i+1]]
        #     t = comb_list[i]
        #     seg[t] = p
        


        #extract topics
        
        # topics = "\n".join(topics)
        

        # point_chunks = ['\n'.join(points[i:i+10]) for i in range(0, len(points), 10)]
        # for pc in point_chunks:
        #     at = self.assign_topics(pc, topics)
        
        # Combine chunk summaries into a final summary
        # final_summary = ''
        # for i in range(len(summaries)):
        #     final_summary = self.create_final_summary([summaries[i],summaries[i+1]])

        # combined = "\n\n".join(summaries[8:])

        # estimate_tokens_simple(summaries[8:])

        # with open("final_summary.txt", "w") as file:
        #     file.write(final_summary)
        
        # return final_summary
        return 1

ul = UseLlama()
TR = transcribe.YouTubeTranscriber()

# tr = TR.get_transcript("nuIgsUM9GgM")
with open('transcript.txt', 'r') as file:
    tr = file.read()

# chunks = split_transcript_by_time(tr, chunk_minutes=10)

sum = ul.summarize_large_transcript(tr)
print(sum)


pass
