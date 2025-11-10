import requests

url = "https://www.searchapi.io/api/v1/search"
params = {
  "engine": "youtube",
  "q": "Fortnite",
  "sp": "CAI",
  "api_key": "SsDXSDpmkRZQ6FpNa2jCub3w"
}

response = requests.get(url, params=params)
print(response.text)


with open("recent_search.txt", "w", encoding="utf-8") as f:
    f.write(response.text)


import requests

url = "https://www.searchapi.io/api/v1/search"
params = {
  "engine": "youtube_transcripts",
  "video_id": "0e3GPea1Tyg",
  "api_key": "SsDXSDpmkRZQ6FpNa2jCub3w"
}

response = requests.get(url, params=params)
print(response.text)
with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(response.text)



import requests

url = "https://www.searchapi.io/api/v1/search"
params = {
  "engine": "youtube_comments",
  "video_id": "jvqFAi7vkBc",
  "api_key": "SsDXSDpmkRZQ6FpNa2jCub3w"
}

response = requests.get(url, params=params)
print(response.text)
with open("comments.txt", "w", encoding="utf-8") as f:
    f.write(response.text)




