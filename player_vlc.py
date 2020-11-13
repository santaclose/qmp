from vlc import Instance
import time
import os

class Player:
	
	def __init__(self):
		self.Player = Instance('--loop --no-video')
		self.volume = 50
		self.listPlayer = None

	def setPlaylist(self, playlist):

		if self.listPlayer != None:
			self.listPlayer.stop()
			self.listPlayer.release()

		self.mediaList = self.Player.media_list_new()
		for song in playlist:
			self.mediaList.add_media(self.Player.media_new(song))
		self.listPlayer = self.Player.media_list_player_new()
		self.listPlayer.set_media_list(self.mediaList)
		self.listPlayer.get_media_player().audio_set_volume(self.volume)

	def play(self, index):
		self.listPlayer.play_item_at_index(index)

	def next(self):
		self.listPlayer.next()
	
	def pause(self):
		self.listPlayer.pause()
	
	def previous(self):
		self.listPlayer.previous()
	
	def stop(self):
		self.listPlayer.stop()
	
	def setPosition(self, v):
		self.listPlayer.get_media_player().set_position(v)

	def setVolume(self, v):
		self.volume = int(v * 100)
		if self.listPlayer != None:
			self.listPlayer.get_media_player().audio_set_volume(self.volume)

	def addToQueue(self, song):
		self.mediaList.add_media(self.Player.media_new(song))