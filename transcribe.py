'''
https://github.com/jdepoix/youtube-transcript-api
'''
from youtube_transcript_api import YouTubeTranscriptApi
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
            transcript = self.supadata.transcript(
                url=video_url,
                lang="en",  # Optional: preferred language
                text=False,  # Optional: return plain text instead of timestamped chunks
                mode="auto"  # Optional: "native", "auto", or "generate"
            )
            return transcript
        except SupadataError as e:
            print(f"Error fetching transcript: {e}")
            return None






