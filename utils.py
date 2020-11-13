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

# returns array with format: [[ArtistName, AlbumListPath]...]
def fetchArtists(url):
	fileContents = fetchFile(url)
	return [x.split("\\") for x in fileContents.split("\n") if len(x) > 0]

# returns array with format: [[AlbumName, AlbumPath, ImagePath]...]
def fetchAlbums(url):
	fileContents = fetchFile(url)
	return [x.split("\\") for x in fileContents.split("\n") if len(x) > 0]

# returns array with format: [[SongName, mp3url]...]
def fetchSongs(url):
	fileContents = fetchFile(url)
	return [x.split("\\") for x in fileContents.split("\n")[1:] if len(x) > 0]


# returns array with format: [[PlaylistName, PlaylistPath]...]
def fetchPlaylists(url):
	fileContents = fetchFile(url)
	return [x.split("\\") for x in fileContents.split("\n") if len(x) > 0]

# returns array with format: [[Song, Artist, Album, mp3url]...]
def fetchPlaylistSongs(url):
	fileContents = fetchFile(url)
	return [x.split("\\") for x in fileContents.split("\n") if len(x) > 0]

# returns the mp3 file in a byte array
def fetchMp3(url):
	result = subprocess.run(['wget', url, '-O', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
	return result.stdout