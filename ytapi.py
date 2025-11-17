from pathlib import Path
from typing import Any
import yaml
import sys
from datetime import datetime, timedelta
import requests

CRED_PATH = './credentials.yaml'

def read_yaml(path: str | Path) -> Any:
    """
    Read a YAML file and return the parsed Python object.
    Raises FileNotFoundError or yaml.YAMLError on error.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"YAML file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
pass

cred = read_yaml(CRED_PATH)
API_KEY = cred.get("youtube_data_api")
max_results=50
query = "AI economy | artificial intelligence economy | AI economic impact"

assert API_KEY , "You must set your YouTube Data API key in credentials.yaml"

one_week_ago = (datetime.now() - timedelta(days=7)).isoformat() + "Z"
base_url = "https://www.googleapis.com/youtube/v3/search"
params = {
    'part': 'snippet',
    'q': query,
    'type': 'video',
    'publishedAfter': one_week_ago,
    'maxResults': max_results,
    'order': 'viewCount',  # Sort by view count
    'relevanceLanguage': 'en',
    'videoDuration': 'long',
    'key': API_KEY
}
response = requests.get(base_url, params=params)
data = response.json()
video_ids = []

for item in data['items']:
    video_id = item['id']['videoId']
    stats_url = "https://www.googleapis.com/youtube/v3/videos"
    stats_params = {
        'part': 'statistics',
        'id': video_id,
        'key': API_KEY
    }
    stats_response = requests.get(stats_url, params=stats_params)
    stats_data = stats_response.json()
    if stats_data['items']:
        view_count = int(stats_data['items'][0]['statistics'].get('viewCount', 0))
        if view_count > 10000:
            video_ids.append({
                'video_id': video_id,
                'title': item['snippet']['title'],
                'views': view_count,
                'published_at': item['snippet']['publishedAt']
            })
    pass







    
