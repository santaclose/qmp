import os, sys, urllib.request, json
import utils
import link_provider
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

		self.selectedArtist = -1
		self.selectedAlbum = -1

		self.artistDat = None
		self.albumDat = None
		self.songDat = None

		self.filterMap = None
		self.filteredIndices = None
		self.filtered = False
		
		self.playlistDat = None
		self.selectedPlaylist = -1
		self.playlistSongDat = None
		self.currentlyPlayingPlaylist = None

	def updateStringModel(self, model, list):
		model.setStringList([item.replace('&', '&&') for item in list])

	def fixIndexIfFiltered(self, index):
		return index if not self.filtered else self.filterMap[self.filteredList[index]]

	def GoBack(self):
		if self.state == self.LIBRARY_STATE:
			if self.libState > self.ARTIST_SELECTION:
				self.libState -= 1
				if self.libState == self.ALBUM_SELECTION:
					self.updateStringModel(self.listViewModel, [item[0] for item in self.albumDat])
				else: # artist selection
					self.updateStringModel(self.listViewModel, [item[0] for item in self.artistDat])
				self.filtered = False
		else:
			self.LoadPlaylists()

	def OnItemSelected(self, index):
		index = int(index)

		if self.state == self.LIBRARY_STATE:
			if self.libState < self.SONG_SELECTION:
				self.libState += 1
				if self.libState == self.ALBUM_SELECTION:
					self.selectedArtist = self.fixIndexIfFiltered(index)
					self.albumDat = utils.fetchAlbums(self.artistDat[self.selectedArtist][1])
					self.updateStringModel(self.listViewModel, [item[0] for item in self.albumDat])
				else: # song selection
					self.selectedAlbum = self.fixIndexIfFiltered(index)
					self.songDat = utils.fetchSongs(self.albumDat[self.selectedAlbum][1])
					self.updateStringModel(self.listViewModel, [item[0] for item in self.songDat])
				self.filtered = False
			else: # play the selected song
				selectedSong = self.fixIndexIfFiltered(index)
				self.player.setPlaylist([item[1] for item in self.songDat])
				self.player.play(selectedSong)
		else:
			if self.playlistState == self.PLAYLIST_SELECTION:
				self.selectedPlaylist = self.fixIndexIfFiltered(index)
				self.playlistSongDat = utils.fetchPlaylistSongs(self.playlistDat[self.selectedPlaylist][1])
				self.updateStringModel(self.listViewModel, [item[0] for item in self.playlistSongDat])
				self.playlistState += 1
			else:
				selectedSong = self.fixIndexIfFiltered(index)
				self.player.setPlaylist([item[3] for item in self.playlistSongDat])
				self.player.play(selectedSong)
				self.currentlyPlayingPlaylist = self.playlistDat[self.selectedPlaylist][0]

	def LoadArtists(self):
		self.filtered = False
		self.state = self.LIBRARY_STATE
		self.libState = self.ARTIST_SELECTION
		self.artistDat = utils.fetchArtists(self.config["libraryRoot"])
		self.updateStringModel(self.listViewModel, [item[0] for item in self.artistDat])

	def LoadPlaylists(self):
		self.filtered = False
		self.state = self.PLAYLIST_STATE
		self.playlistState = self.PLAYLIST_SELECTION
		self.playlistDat = utils.fetchPlaylists(self.config["playlistRoot"])
		self.updateStringModel(self.listViewModel, [item[0] for item in self.playlistDat])

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

	def generateFilterData(self, dat, index, text):
		itemList = [item[index] for item in dat]
		for i in range(len(itemList)):
			if text.lower() in itemList[i].lower():
				self.filteredList.append(itemList[i]) 
				self.filterMap[itemList[i]] = i
	def OnSearch(self, text):
		self.filtered = True
		self.filteredList = []
		self.filterMap = {}
		if self.state == self.LIBRARY_STATE:
			if self.libState == self.ARTIST_SELECTION:
				self.generateFilterData(self.artistDat, 0, text)
			elif self.libState == self.ALBUM_SELECTION:
				self.generateFilterData(self.albumDat, 0, text)
			else: # song selection
				self.generateFilterData(self.songDat, 0, text)
		else: # playlist state
			if self.playlistState == self.PLAYLIST_SELECTION:
				self.generateFilterData(self.playlistDat, 0, text)
			else: # playlist song selection
				self.generateFilterData(self.playlistSongDat, 0, text)
		self.updateStringModel(self.listViewModel, self.filteredList)


	def CopyMp3Url(self, index):
		index = self.fixIndexIfFiltered(index)
		if self.state == self.LIBRARY_STATE:
			pyperclip.copy(self.songDat[index][1])
		else:
			pyperclip.copy(self.playlistSongDat[index][3])
	def CopyYoutubeUrl(self, index):
		index = self.fixIndexIfFiltered(index)
		if "googleApiKey" not in self.config:
			print("Google api key not found in config.json")
			return
		if self.state == self.LIBRARY_STATE:
			searchText = self.songDat[index][0] + f" {self.artistDat[self.selectedArtist][0]}"
			pyperclip.copy(link_provider.getYoutubeLink(searchText, self.config["googleApiKey"]))
		else: # playlists state
			searchText = self.playlistSongDat[index][0] + f" {self.playlistSongDat[index][1]}"
			pyperclip.copy(link_provider.getYoutubeLink(searchText, self.config["googleApiKey"]))

	def AddToQueue(self, index):
		index = self.fixIndexIfFiltered(index)
		if self.state == self.LIBRARY_STATE:
			self.player.addToQueue(self.songDat[index][1])
		else:
			self.player.addToQueue(self.playlistSongDat[index][3])

	def GetPlaylists(self):
		self.playlistDat = utils.fetchPlaylists(self.config["playlistRoot"])
		self.updateStringModel(self.playlistListViewModel, [item[0] for item in self.playlistDat])

	def AddToPlaylist(self, playlistIndex, songIndex):
		if self.playlistDat[playlistIndex][0] == self.currentlyPlayingPlaylist:
			self.AddToQueue(songIndex)

		songIndex = self.fixIndexIfFiltered(songIndex)
		# playlist element format: songName\artistName\albumName\songURL
		if self.state == self.LIBRARY_STATE:
			lineToWrite = self.songDat[songIndex][0] + '\\' + self.artistDat[self.selectedArtist][0] + '\\' + self.albumDat[self.selectedAlbum][0] + '\\' + self.songDat[songIndex][1]
		else:
			lineToWrite = self.playlistSongDat[songIndex][0] + '\\' + self.playlistSongDat[songIndex][1] + '\\' + self.playlistSongDat[songIndex][2] + '\\' + self.playlistSongDat[songIndex][3]
		with open(self.playlistDat[playlistIndex][1], 'a+') as file:
			file.write(lineToWrite + '\n')