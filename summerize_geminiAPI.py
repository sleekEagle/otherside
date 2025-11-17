from google import genai
from helper import read_yaml
from transcribe import YouTubeTranscriber

# ytt = YouTubeTranscriber()
# tr = ytt.get_transcript("https://www.youtube.com/watch?v=nuIgsUM9GgM")
# tr.content
# with open("transcript.txt", "w", encoding="utf-8") as f:
#     f.write(tr.content)

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
