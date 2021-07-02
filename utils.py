from urllib.request import urlopen
from difflib import SequenceMatcher
import subprocess

def htmlize(searchText):
	return searchText.replace(' ', '%20')

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
	return [{"ArtistName": x.split("\\")[0], "AlbumListPath": x.split("\\")[1]} for x in fileContents.split("\n") if len(x) > 0]

def fetchAlbums(url):
	fileContents = fetchFile(url)
	return [{"AlbumName": x.split("\\")[0], "AlbumPath": x.split("\\")[1], "ImagePath": x.split("\\")[2]} for x in fileContents.split("\n") if len(x) > 0]

def fetchSongs(url):
	fileContents = fetchFile(url)
	return [{"SongName": x.split("\\")[0], "AudioPath": x.split("\\")[1]} for x in fileContents.split("\n")[1:] if len(x) > 0]


def fetchPlaylists(url):
	fileContents = fetchFile(url)
	return [{"PlaylistName": x.split("\\")[0], "PlaylistPath": x.split("\\")[1]} for x in fileContents.split("\n") if len(x) > 0]

def fetchPlaylistSongs(url):
	fileContents = fetchFile(url)
	return [{"SongName": x.split("\\")[0], "ArtistName": x.split("\\")[1], "AlbumName": x.split("\\")[2], "AudioPath": x.split("\\")[3]} for x in fileContents.split("\n") if len(x) > 0]

# returns the mp3 file in a byte array (not curretly being used)
def fetchMp3(url):
	result = subprocess.run(['wget', url, '-O', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
	return result.stdout