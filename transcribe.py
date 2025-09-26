'''
https://github.com/jdepoix/youtube-transcript-api
'''
from youtube_transcript_api import YouTubeTranscriptApi

# video_id = "yKuwrnCfsFQ"  # The part after "v=" in YouTube URL
# tr = get_trancript_ytTapi(video_id)
# for snippet in tr:
#     print(snippet.text)

def get_trancript_ytTapi(video_id):
    ytt_api = YouTubeTranscriptApi()
    tr = ytt_api.fetch(video_id)
    return tr



