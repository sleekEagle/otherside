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
            Create a concise bullet point summary from this timestamped transcript by following these rules:

            1. **Group related content**: Combine consecutive sections that discuss the same topic or theme
            2. **Use earliest timestamp**: For each grouped section, use the first timestamp as the reference
            3. **Be concise**: Each bullet should be a single sentence summarizing the main point
            4. **Maintain flow**: Keep the chronological progression of ideas
            5. **Output format**: Strictly use `[HH:MM:SS] summary text`

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


