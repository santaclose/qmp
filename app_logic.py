import os, sys, urllib.request, json
import utils
import player_vlc as player_module
import pyperclip

class AppLogic():
	def __init__(self, listViewModel, playlistListViewModel):
		self.LIBRARY_STATE = 0
		self.PLAYLIST_STATE = 1
		self.state = 0

		self.ARTIST_SELECTION = 0
		self.ALBUM_SELECTION = 1
		self.SONG_SELECTION = 2
		self.libState = 0

		self.PLAYLIST_SELECTION = 0
		self.PLAYLIST_SONG_SELECTION = 1
		self.playlistState = 0

		self.listViewModel = listViewModel
		self.playlistListViewModel = playlistListViewModel
		with open("config.json", 'r') as file:
			self.config = json.loads(file.read())
		self.player = player_module.Player()

		self.selectedArtist = None
		self.selectedAlbum = None
		self.artistsDict = None
		self.albumsDict = None
		self.songDict = None
		self.filteredList = None
		self.filtered = False
		
		self.playlistsDict = None
		self.selectedPlaylist = None
		self.playlistSongsDict = None

	def GoBack(self):
		if self.state == self.LIBRARY_STATE:
			if self.libState > self.ARTIST_SELECTION:
				self.libState -= 1
				if self.libState == self.ALBUM_SELECTION:
					self.listViewModel.setStringList(list(self.albumsDict.keys()))
				else: # artist selection
					self.listViewModel.setStringList(list(self.artistsDict.keys()))
				self.filtered = False
		else:
			self.LoadPlaylists()

	def OnItemSelected(self, index):
		index = int(index)

		if self.state == self.LIBRARY_STATE:
			if self.libState < self.SONG_SELECTION:
				self.libState += 1
				if self.libState == self.ALBUM_SELECTION:
					self.selectedArtist = list(self.artistsDict.keys())[index] if not self.filtered else self.filteredList[index]
					self.albumsDict = utils.fetchAlbums(self.artistsDict[self.selectedArtist])
					self.listViewModel.setStringList(list(self.albumsDict.keys()))
				else: # song selection
					self.selectedAlbum = list(self.albumsDict.keys())[index] if not self.filtered else self.filteredList[index]
					self.songDict = utils.fetchSongs(self.albumsDict[self.selectedAlbum])
					self.listViewModel.setStringList(list(self.songDict.keys()))
				self.filtered = False
			else: # play the selected song
				self.player.setPlaylist(list(self.songDict.values()))
				self.player.play(index)
		else:
			if self.playlistState == self.PLAYLIST_SELECTION:
				self.selectedPlaylist = list(self.playlistsDict.keys())[index]
				self.playlistSongsDict = utils.fetchPlaylistSongs(self.playlistsDict[self.selectedPlaylist])
				self.listViewModel.setStringList(list(self.playlistSongsDict.keys()))
				self.playlistState += 1
			else:
				self.player.setPlaylist(list(self.playlistSongsDict.values()))
				self.player.play(index)

	def LoadArtists(self):
		self.state = self.LIBRARY_STATE
		self.libState = self.ARTIST_SELECTION
		self.artistsDict = utils.fetchArtists(self.config["musicRoot"])
		self.listViewModel.setStringList(list(self.artistsDict.keys()))

	def LoadPlaylists(self):
		self.state = self.PLAYLIST_STATE
		self.playlistState = self.PLAYLIST_SELECTION
		self.playlistsDict = utils.fetchPlaylists(self.config["playlistRoot"])
		self.listViewModel.setStringList(list(self.playlistsDict.keys()))

	def SetVolume(self, value):
		self.player.setVolume(value)

	def SetPosition(self, value):
		self.player.setPosition(value)

	def Prev(self):
		self.player.previous()

	def Pause(self):
		self.player.pause()

	def Next(self):
		self.player.next()

	def OnSearch(self, text):
		self.filtered = True
		self.filteredList = []
		if self.libState == self.ARTIST_SELECTION:
			artistList = list(self.artistsDict.keys())
			for i in range(len(artistList)):
				if text.lower() in artistList[i].lower():
					self.filteredList.append(artistList[i]) 
			self.listViewModel.setStringList(self.filteredList)
		elif self.libState == self.ALBUM_SELECTION:
			albumList = list(self.albumsDict.keys())
			for i in range(len(albumList)):
				if text.lower() in albumList[i].lower():
					self.filteredList.append(albumList[i]) 
			self.listViewModel.setStringList(self.filteredList)

	def CopyMp3Url(self, index):
		pyperclip.copy(list(self.songDict.values())[index])

	def GetPlaylists(self):
		self.playlistsDict = utils.fetchPlaylists(self.config["playlistRoot"])
		self.playlistListViewModel.setStringList(list(self.playlistsDict.keys()))

	def AddToPlaylist(self, playlistIndex, songIndex):
		string = list(self.songDict.keys())[songIndex] + "\\" + self.selectedArtist + "\\" + self.selectedAlbum + "\\" + list(self.songDict.values())[songIndex]
		with open(list(self.playlistsDict.values())[playlistIndex], 'a+') as file:
			file.write(string + '\n')