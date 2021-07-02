from urllib.request import urlopen
from difflib import SequenceMatcher
from github import Github
import subprocess
import json
import re


config = None
try:
	with open("config.json", 'r') as file:
		configContent = file.read()
except:
	print("Configuration file does not exist, creating one")
	with open("config.json", "a+") as file:
		file.write('{\n\t"libraryRoot": "",\n\t"playlistRoot": "",\n\t"googleApiKey": ""\n\t"githubToken": ""\n\t"playlistFolder": ""\n}')
	exit()
try:
	config = json.loads(configContent)
	print("Configuration file loaded")
except:
	print("Invalid json file")


def nameToDirectoryName(name):
	out = ''
	availableCharacters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	for char in name:
		if char in availableCharacters:
			out += char
		elif char == ' ':
			out += '_'
	return out

def htmlize(searchText):
	return searchText.replace(' ', '%20')

def similar(a, b):
	return SequenceMatcher(None, a, b).ratio()

def readFile(resource):
	if resource.startswith("http://") or resource.startswith("https://"):
		return urlopen(resource).read().decode('utf-8').replace('\r', '');
	else:
		with open(resource, 'r') as file:
			contents = file.read()
		return contents.replace('\r', '')

def writeFile(resource, contents):
	if resource.startswith("http://") or resource.startswith("https://"):
		searchResult = re.search(r"^https?://raw.githubusercontent.com/([^/]+)/([^/]+)/([^/]+)/(.+)$", resource)
		githubUser = searchResult.group(1)
		githubRepo = searchResult.group(2)
		githubBranch = searchResult.group(3)
		githubFile = searchResult.group(4)
		g = Github(config['githubToken'])
		repo = g.get_user().get_repo(githubRepo)

		# create or update accordingly
		try:
			file = repo.get_contents(githubFile)
			repo.update_file(githubFile, f"update {githubFile}", contents, file.sha)
		except:
			repo.create_file(githubFile, f"create {githubFile}", contents)
			pass
	else:
		with open(resource, 'w') as file:
			file.write(contents)


def fetchArtists(url):
	fileContents = readFile(url)
	return [{"ArtistName": x.split("\\")[0], "AlbumListPath": x.split("\\")[1]} for x in fileContents.split("\n") if len(x) > 0]

def fetchAlbums(url):
	fileContents = readFile(url)
	return [{"AlbumName": x.split("\\")[0], "AlbumPath": x.split("\\")[1], "ImagePath": x.split("\\")[2]} for x in fileContents.split("\n") if len(x) > 0]

def fetchSongs(url):
	fileContents = readFile(url)
	return [{"SongName": x.split("\\")[0], "AudioPath": x.split("\\")[1]} for x in fileContents.split("\n")[1:] if len(x) > 0]


def fetchPlaylists(url):
	fileContents = readFile(url)
	return [{"PlaylistName": x.split("\\")[0], "PlaylistPath": x.split("\\")[1]} for x in fileContents.split("\n") if len(x) > 0]

def fetchPlaylistSongs(url):
	fileContents = readFile(url)
	return [{"SongName": x.split("\\")[0], "ArtistName": x.split("\\")[1], "AlbumName": x.split("\\")[2], "AudioPath": x.split("\\")[3]} for x in fileContents.split("\n") if len(x) > 0]

# returns the mp3 file in a byte array (not curretly being used)
def fetchMp3(url):
	result = subprocess.run(['wget', url, '-O', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
	return result.stdout