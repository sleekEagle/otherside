'''
https://github.com/jdepoix/youtube-transcript-api
'''
from supadata import Supadata, SupadataError
from helper import read_yaml


# video_id = "yKuwrnCfsFQ"  # The part after "v=" in YouTube URL
# tr = get_trancript_ytTapi(video_id)
# for snippet in tr:
#     print(snippet.text)

# def get_trancript_ytTapi(video_id):
#     ytt_api = YouTubeTranscriptApi()
#     tr = ytt_api.fetch(video_id)
#     return tr

def ms_to_timestamp(ms):
    ms = int(ms)
    seconds = ms // 1000
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

class YouTubeTranscriber:
    def __init__(self):
        CRED_PATH = './credentials.yaml'
        cred = read_yaml(CRED_PATH)
        SUPADATA_KEY = cred.get("supadata")
        assert SUPADATA_KEY , "You must set your Supadata API key in credentials.yaml"
        self.supadata = Supadata(api_key=SUPADATA_KEY)
    
    '''
    how to use get_transcript_supadata:
    tr = get_transcript_supadata("https://www.youtube.com/watch?v=nuIgsUM9GgM")
    get string of the transcript: 
    tr.content
    '''
    def get_transcript(self, video_url: str):
        try:
            if not video_url.startswith("https://www.youtube.com/watch?v="):
                video_url = f"https://www.youtube.com/watch?v={video_url}"
            transcript = self.supadata.transcript(
                url=video_url,
                lang="en",  # Optional: preferred language
                text=False,  # Optional: return plain text instead of timestamped chunks
                mode="auto"  # Optional: "native", "auto", or "generate"
            )
            return self.convert_supadata_chunks(transcript.content)
        except SupadataError as e:
            print(f"Error fetching transcript: {e}")
            return None
        
    def convert_supadata_chunks(self, chunks):
        lines = []
        for entry in chunks:
            offset = entry.offset
            ts = ms_to_timestamp(offset)
            text = entry.text
            line = f"[{ts}] {text}"
            lines.append(line)
        return "\n".join(lines)






