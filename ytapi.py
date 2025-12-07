from pathlib import Path
from typing import Any
import yaml
import sys
from datetime import datetime, timedelta
import requests
from helper import read_yaml
import json

CRED_PATH = './credentials.yaml'
    
cred = read_yaml(CRED_PATH)
API_KEY = cred.get("youtube_data_api")
assert API_KEY , "You must set your YouTube Data API key in credentials.yaml"
MAX_RESULTS=50

query = "AI|artificial intelligence|AI economy|artificial intelligence economy|AI economic impact -tutorial -review -lecture"
    
def get_videos(query: str, nextpage: str = None):
    one_week_ago = (datetime.now() - timedelta(days=30)).isoformat() + "Z"
    base_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'publishedAfter': one_week_ago,
        'maxResults': MAX_RESULTS,
        # 'order': 'viewCount',  # Sort by view count
        'relevanceLanguage': 'en',
        'videoDuration': 'long',
        'key': API_KEY
    }
    if nextpage:
        params['pageToken'] = nextpage

    response = requests.get(base_url, params=params)
    data = response.json()
    nxtpg = data.get('nextPageToken')
    
    video_ids = []
    for i,item in enumerate(data['items']):
        print(f'Processing video: {i} of {len(data["items"])}', end='\r')
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
            if view_count > 5000:
                video_ids.append({
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'views': view_count,
                    'published_at': item['snippet']['publishedAt']
                })
    return video_ids, nxtpg

def search_videos(query: str):
    video_id_list = []
    N_VIDEOS = 200
    video_ids, nextpage = get_videos(query)
    video_id_list.extend(video_ids)
    while len(video_ids)>0 and nextpage is not None:
        video_ids, nextpage = get_videos(query, nextpage)
        video_id_list.extend(video_ids)
        if len(video_id_list) >= N_VIDEOS:
            break
    return video_id_list


video_id_list = search_videos(query)
with open("search.json", "w") as f:
    json.dump(video_id_list, f, indent=2)  # indent for pretty printing

with open("search.json", "r") as f:
    loaded_data = json.load(f)





    
