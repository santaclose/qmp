import requests
import json
import utils

def getYoutubeLink(searchText, apiKey):
	searchText = utils.fixUrlText(searchText)
	r = requests.get(f"https://youtube.googleapis.com/youtube/v3/search?q={searchText}&key={apiKey}")
	jsonObject = json.loads(r.text)
	videoId = jsonObject["items"][0]["id"]["videoId"]
	return f"https://www.youtube.com/watch?v={videoId}"