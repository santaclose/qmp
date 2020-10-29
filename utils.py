from urllib.request import urlopen
from difflib import SequenceMatcher
import subprocess

def similar(a, b):
	return SequenceMatcher(None, a, b).ratio()

def fetchFile(resource):
	if resource.startswith("http://") or resource.startswith("https://"):
		return urlopen(resource).read().decode('utf-8').replace('\r', '');
	else:
		file = open(resource, 'r')
		fileContents = file.read()
		file.close()
		return fileContents.replace('\r', '')

def fetchArtists(url):
	fileContents = fetchFile(url)
	return dict(x.split("\\") for x in fileContents.split("\n") if len(x) > 0)
	
def fetchAlbums(url):
	fileContents = fetchFile(url)
	return dict(x.split("\\")[:-1] for x in fileContents.split("\n") if len(x) > 0)

def fetchSongs(url):
	fileContents = fetchFile(url)
	return dict(x.split("\\") for x in fileContents.split("\n")[1:] if len(x) > 0)

def fetchMp3(url):
	# log = open("log.log", 'w')
	# log.write(url)
	# log.close()
	
	result = subprocess.run(['wget', url, '-O', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
	return result.stdout

def fetchPlaylists(url):
	fileContents = fetchFile(url)
	return dict(x.split("\\") for x in fileContents.split("\n") if len(x) > 0)

def fetchPlaylistSongs(url):
	fileContents = fetchFile(url)
	return dict([x.split("\\")[0], x.split("\\")[3]] for x in fileContents.split("\n") if len(x) > 0)
