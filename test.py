from llama_cpp import Llama
import transcribe
import os
import re
import platform
from openai import OpenAI

def estimate_tokens_simple(text: str) -> int:
    """
    Rough estimation: 1 token ≈ 4 characters for English text
    For more accuracy: 1 token ≈ 0.75 words
    """
    # Method 1: Character-based
    char_count = len(text)
    token_estimate_chars = char_count / 4
    
    # Method 2: Word-based
    word_count = len(text.split())
    token_estimate_words = word_count / 0.75
    
    # Return average
    return int((token_estimate_chars + token_estimate_words) / 2)



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
        self.client = OpenAI(
            base_url="http://localhost:8080/v1",
            api_key="local-llama"   # ignored, but required
        )
    
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
        prompt = f"""Analyze this YouTube transcript segment (Chunk {chunk_num}):

        TRANSCRIPT:
        {chunk_text}

        TASK: Extract key points with their INDIVIDUAL starting timestamps.

        INSTRUCTIONS:
        1. Identify distinct key points discussed in this segment
        2. For EACH point, find the EXACT timestamp when that point STARTS being discussed
        3. Each point must be a complete sentence

        OUTPUT FORMAT:
        • [Point 1 sentence] (starts at 12:34)
        • [Point 2 sentence] (starts at 15:20)
        • [Point 3 sentence] (starts at 18:45)

        IMPORTANT:
        - Each timestamp should mark when THAT SPECIFIC POINT begins
        - Use "starts at [timestamp]" format for clarity
        - Points should be distinct, not overlapping in content
        - Include as many relevant points as possible from this segment

        Now analyze the transcript segment above and extract points with their individual starting timestamps."""
            
        # messages = [
        #         {"role": "system", "content": "You summarize transcript segments with their starting timestamps."},
        #         {"role": "user", "content": prompt}
        #     ]
            
        # response = self.llm.create_chat_completion(
        #         messages=messages,
        #         temperature=0.2,
        #         max_tokens=800
        #     )
        ret = self.request("You summarize transcript segments with their starting timestamps.", prompt, 800)
        
            
        return ret
    
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

        final_summary = self.create_final_summary(summaries)

        combined = "\n\n".join(summaries)
        len(combined.split('\n'))
        
        # Combine chunk summaries into a final summary
        # final_summary = ''
        # for i in range(len(summaries)):
        #     final_summary = self.create_final_summary([summaries[i],summaries[i+1]])

        # combined = "\n\n".join(summaries[8:])

        # estimate_tokens_simple(summaries[8:])

        with open("final_summary.txt", "w") as file:
            file.write(final_summary)
        
        return final_summary

ul = UseLlama()
TR = transcribe.YouTubeTranscriber()

# tr = TR.get_transcript("nuIgsUM9GgM")
with open('transcript.txt', 'r') as file:
    tr = file.read()

# chunks = split_transcript_by_time(tr, chunk_minutes=10)

sum = ul.summarize_large_transcript(tr)
print(sum)


pass
