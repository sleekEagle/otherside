from google import genai
from helper import read_yaml
import re

class SummerizeGeminiAPI:
    def __init__(self):
        CRED_PATH = './credentials.yaml'   
        cred = read_yaml(CRED_PATH)
        API_KEY = cred.get("gemini")
        self.client = genai.Client(api_key=API_KEY)

    def summerize(self, transcript: str) -> str:
        prompt = f"""
            Create a concise bullet point summary from this timestamped transcript following EXACTLY these rules:

            **CONTENT FILTERING RULES:**
            1. **SKIP INTRODUCTIONS**: Ignore opening sections like "Welcome to...", "In this video...", "Today we'll cover..."
            2. **SKIP OUTROS**: Ignore closing sections like "Thanks for watching", "Please subscribe", "Check the description"
            3. **SKIP PROMOTIONS**: Ignore promotional content, channel plugs, sponsor messages
            4. **SKIP AUDIENCE ENGAGEMENT**: Ignore "like/share/subscribe", calls to action, engagement requests
            5. **FOCUS ON SUBSTANCE**: Only include substantive educational/informative content

            **SUMMARIZATION RULES:**
            1. **GROUP RELATED CONTENT**: Combine consecutive sections discussing the same topic
            2. **USE EARLIEST TIMESTAMP**: For each grouped section, use the first timestamp as reference
            3. **BE CONCISE**: Each bullet must be a single sentence with ONLY the main point
            4. **MAINTAIN FLOW**: Keep chronological progression of core content only
            5. **STRICT FORMAT**: Output ONLY in this format: `[HH:MM:SS] summary text`
            6. **NO NARRATION**: Do NOT use phrases like "the speaker", "the video", "he/she says" - state the content directly
            7. **CLEAN OUTPUT**: Output ONLY the bullet points, nothing before or after

            **EXAMPLES OF CONTENT TO SKIP:**
            - "Welcome back to my channel"
            - "Before we begin, please subscribe"
            - "Today I'll teach you about..."
            - "Don't forget to hit the like button"
            - "Thanks for watching, see you next time"
            - "Check out my other videos"
            - "This video is sponsored by..."

            **Transcript:**
            {transcript}
            """
        response = self.client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return response.text
    
    def parse_summary(self, summary: str) -> list:
        # assuming summary is in bullet points
        lines_sep = []
        lines = summary.split('\n')
        for line in lines:
            match = re.match(r"\[(\d{1,2}:\d{2}:\d{2})\]\s*(.*)", line.strip())
            if match:
                timestamp = match.group(1)   # "00:03:50"
                text = match.group(2) 
                lines_sep.append({"timestamp": timestamp, "text": text})
        return lines_sep
            
    
'''
ytt = YouTubeTranscriber()
tr = ytt.get_transcript("https://www.youtube.com/watch?v=nuIgsUM9GgM")
with open("transcript.txt", "w") as file:
    file.write(tr)
'''

# with open('transcript.txt', 'r') as file:
#     transcript = file.read()

# summerizer = SummerizeGeminiAPI()
# sum = summerizer.summerize(transcript)

# with open("summary.txt", "w") as file:
#     file.write(sum)

# with open('summary.txt', 'r') as file:
#     sum = file.read()

# parsed_summary = summerizer.parse_summary(sum)

def generate_summaries():
    import json 
    import os

    with open("search.json", "r") as f:
        search_data = json.load(f)

    import transcribe
    import os
    TR = transcribe.YouTubeTranscriber()
    summerizer = SummerizeGeminiAPI()
    os.makedirs("summary", exist_ok=True)

    files = os.listdir("summary")
    files = [f.split('.')[0] for f in files]

    for i,search in enumerate(search_data):
        vid_id = search['video_id']
        if vid_id in files:
            continue
        print(f"Processing video {i+1} of {len(search_data)}", end='\r')
        video_id = search['video_id']
        ytt = TR.get_transcript(video_id)
        sum = summerizer.summerize(ytt)
        with open(f"summary/{video_id}.txt", "w", encoding="utf-8") as file:
            file.write(sum)


def generate_final_summary():
    #create the prrompt
    with open("prompts/final_summary.txt", 'r', encoding="utf-8") as f:
            prompt = f.read()

    with open("summary/all_summaries.txt", 'r', encoding="utf-8") as f:
            concat_summary = f.read()

    search_text = 'INPUT DATA START'
    index = prompt.find(search_text)
    insert_pos = index + len(search_text)
    final_prompt = prompt[:insert_pos] + concat_summary + prompt[insert_pos:]

    

    pass


generate_final_summary()





