import player_vlc as player_module
import link_provider
import pyperclip
import utils

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
					self.updateStringModel(self.listViewModel, [item["AlbumName"] for item in self.albumDat])
				else: # artist selection
					self.updateStringModel(self.listViewModel, [item["ArtistName"] for item in self.artistDat])
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
					self.albumDat = utils.fetchAlbums(self.artistDat[self.selectedArtist]["AlbumListPath"])
					self.updateStringModel(self.listViewModel, [item["AlbumName"] for item in self.albumDat])
				else: # song selection
					self.selectedAlbum = self.fixIndexIfFiltered(index)
					self.songDat = utils.fetchSongs(self.albumDat[self.selectedAlbum]["AlbumPath"])
					self.updateStringModel(self.listViewModel, [item["SongName"] for item in self.songDat])
				self.filtered = False
			else: # play the selected song
				selectedSong = self.fixIndexIfFiltered(index)
				self.player.setPlaylist([item["AudioPath"] for item in self.songDat])
				self.player.play(selectedSong)
		else:
			if self.playlistState == self.PLAYLIST_SELECTION:
				self.selectedPlaylist = self.fixIndexIfFiltered(index)
				self.playlistSongDat = utils.fetchPlaylistSongs(self.playlistDat[self.selectedPlaylist]["PlaylistPath"])
				self.updateStringModel(self.listViewModel, [item["SongName"] for item in self.playlistSongDat])
				self.playlistState += 1
			else:
				selectedSong = self.fixIndexIfFiltered(index)
				self.player.setPlaylist([item["AudioPath"] for item in self.playlistSongDat])
				self.player.play(selectedSong)
				self.currentlyPlayingPlaylist = self.playlistDat[self.selectedPlaylist]["PlaylistName"]

	def LoadArtists(self):
		self.filtered = False
		self.state = self.LIBRARY_STATE
		self.libState = self.ARTIST_SELECTION
		self.artistDat = utils.fetchArtists(utils.config["libraryRoot"])
		self.updateStringModel(self.listViewModel, [item["ArtistName"] for item in self.artistDat])

	def LoadPlaylists(self):
		self.filtered = False
		self.state = self.PLAYLIST_STATE
		self.playlistState = self.PLAYLIST_SELECTION
		self.playlistDat = utils.fetchPlaylists(utils.config["playlistRoot"])
		self.updateStringModel(self.listViewModel, [item["PlaylistName"] for item in self.playlistDat])

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

	def generateFilterData(self, itemList, text):
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
				self.generateFilterData([item["ArtistName"] for item in self.artistDat], text)
			elif self.libState == self.ALBUM_SELECTION:
				self.generateFilterData([item["AlbumName"] for item in self.albumDat], text)
			else: # song selection
				self.generateFilterData([item["SongName"] for item in self.songDat], text)
		else: # playlist state
			if self.playlistState == self.PLAYLIST_SELECTION:
				self.generateFilterData([item["PlaylistName"] for item in self.playlistDat], text)
			else: # playlist song selection
				self.generateFilterData([item["SongName"] for item in self.playlistSongDat], text)
		self.updateStringModel(self.listViewModel, self.filteredList)


	def CopyMp3Url(self, index):
		index = self.fixIndexIfFiltered(index)
		if self.state == self.LIBRARY_STATE:
			pyperclip.copy(self.songDat[index]["AudioPath"])
		else:
			pyperclip.copy(self.playlistSongDat[index]["AudioPath"])
	def CopyYoutubeUrl(self, index):
		index = self.fixIndexIfFiltered(index)
		if "googleApiKey" not in utils.config:
			print("Google api key not found in config.json")
			return
		if self.state == self.LIBRARY_STATE:
			searchText = self.songDat[index]["SongName"] + f' {self.artistDat[self.selectedArtist]["ArtistName"]}'
			pyperclip.copy(link_provider.getYoutubeLink(searchText, utils.config["googleApiKey"]))
		else: # playlists state
			searchText = self.playlistSongDat[index]["SongName"] + f' {self.playlistSongDat[index]["ArtistName"]}'
			pyperclip.copy(link_provider.getYoutubeLink(searchText, utils.config["googleApiKey"]))

	def AddToQueue(self, index):
		index = self.fixIndexIfFiltered(index)
		if self.state == self.LIBRARY_STATE:
			self.player.addToQueue(self.songDat[index]["AudioPath"])
		else:
			self.player.addToQueue(self.playlistSongDat[index]["AudioPath"])

	def CreatePlaylist(self, text):
		playlistFolder = utils.config["playlistFolder"]
		playlistFolder += "/" if playlistFolder[-1] != "/" else ""
		pathToNewPlaylist = playlistFolder + utils.nameToDirectoryName(text) + ".dat"
		utils.writeFile(pathToNewPlaylist, "")

		playlistRoot = utils.config["playlistRoot"]
		playlistRootContent = utils.readFile(playlistRoot)
		playlistRootContent += "\n" if len(playlistRootContent) > 0 and playlistRootContent[-1] != "\n" else ""
		playlistRootContent += text + "\\" + pathToNewPlaylist
		utils.writeFile(playlistRoot, playlistRootContent)

	def GetPlaylists(self):
		self.playlistDat = utils.fetchPlaylists(utils.config["playlistRoot"])
		self.updateStringModel(self.playlistListViewModel, [item["PlaylistName"] for item in self.playlistDat])

	def AddToPlaylist(self, playlistIndex, songIndex):
		if self.playlistDat[playlistIndex]["PlaylistName"] == self.currentlyPlayingPlaylist:
			self.AddToQueue(songIndex)

		songIndex = self.fixIndexIfFiltered(songIndex)
		# playlist element format: songName\artistName\albumName\songURL
		if self.state == self.LIBRARY_STATE:
			lineToWrite = self.songDat[songIndex]["SongName"] + '\\' + self.artistDat[self.selectedArtist]["ArtistName"] + '\\' + self.albumDat[self.selectedAlbum]["AlbumName"] + '\\' + self.songDat[songIndex]["AudioPath"]
		else:
			lineToWrite = self.playlistSongDat[songIndex]["SongName"] + '\\' + self.playlistSongDat[songIndex]["ArtistName"] + '\\' + self.playlistSongDat[songIndex]["AlbumName"] + '\\' + self.playlistSongDat[songIndex]["AudioPath"]

		playlistContent = utils.readFile(self.playlistDat[playlistIndex]["PlaylistPath"])
		playlistContent += "\n" if len(playlistContent) > 0 and playlistContent[-1] != "\n" else ""
		playlistContent += lineToWrite + '\n'
		utils.writeFile(self.playlistDat[playlistIndex]["PlaylistPath"], playlistContent)