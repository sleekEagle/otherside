from google import genai
from helper import read_yaml
from transcribe import YouTubeTranscriber
import json

def ms_to_timestamp(ms):
    seconds = ms // 1000
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

ytt = YouTubeTranscriber()
tr = ytt.get_transcript("https://www.youtube.com/watch?v=nuIgsUM9GgM")
tr.content
def convert_supadata_chunks(chunks):
    lines = []
    for entry in tr.content:
        offset = entry.offset
        ts = ms_to_timestamp(offset)
        duration = entry.duration
        text = entry.text
        line = f"[{ts}] {text}"
        lines.append(line)
    return "\n".join(lines)

tr_ts = convert_supadata_chunks(tr.content)
print(tr_ts)

prompt = f"""
You are summarizing a YouTube transcript.
Use the timestamps from the transcript to create timestamped sections.

OUTPUT FORMAT STRICT:
{{
  "sections": [
    {{
      "start": "00:00:00",
      "title": "Short title",
      "points": ["point 1", "point 2"]
    }}
  ]
}}

Rules:
- Do NOT invent timestamps.
- Only use timestamps exactly as they appear.
- Merge lines into logical sections.

Transcript:
{tr_ts}
"""

CRED_PATH = './credentials.yaml'   
cred = read_yaml(CRED_PATH)
API_KEY = cred.get("gemini")
client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt
)
print(response.text)


class SummerizeGeminiAPI:
    def __init__(self):
        CRED_PATH = './credentials.yaml'   
        cred = read_yaml(CRED_PATH)
        API_KEY = cred.get("gemini")
        self.client = genai.Client(api_key=API_KEY)

    def summerize(self, transcript: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.0-flash", contents=f'summerize the following youtube transcript as bullet points and nothing else: {transcript}'
        )
        return response.text
    
    def parse_summary(self, summary: str) -> list:
        # assuming summary is in bullet points
        lines = summary.split('\n')
        for line in lines:
            first_char = line.lstrip()[0] if line.lstrip() else ""
            #does this belong to the bullet points?
            if first_char != "*":
                continue
            #is this a topic
            if line.count("**")==2:
                pass
            else:
                pass
            pass
    

'''
How to use SummerizeGeminiAPI:
# get transcript first
ytt = YouTubeTranscriber()
tr = ytt.get_transcript("https://www.youtube.com/watch?v=nuIgsUM9GgM")

# summerize
sg = SummerizeGeminiAPI()
summary = sg.summerize(tr.content)

'''

with open('summary.txt', "r", encoding="utf-8-sig") as f:
    transcript = f.read()

sg = SummerizeGeminiAPI()
sg.parse_summary(transcript)
