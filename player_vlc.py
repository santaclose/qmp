from vlc import Instance
import time
import os

class Player:
	
	def __init__(self):
		self.Player = Instance('--loop --no-video')
		self.volume = 50
		self.mainPlayer = None

	def setPlaylist(self, playlist):

		if self.mainPlayer != None:
			self.mainPlayer.stop()
			self.mainPlayer.release()

		self.mediaList = self.Player.media_list_new()
		for song in playlist:
			self.mediaList.add_media(self.Player.media_new(song))
		self.mainPlayer = self.Player.media_list_player_new()
		self.mainPlayer.set_media_list(self.mediaList)
		self.mainPlayer.get_media_player().audio_set_volume(self.volume)

	def play(self, index):
		self.mainPlayer.play_item_at_index(index)

	def next(self):
		self.mainPlayer.next()
	
	def pause(self):
		self.mainPlayer.pause()
	
	def previous(self):
		self.mainPlayer.previous()
	
	def stop(self):
		self.mainPlayer.stop()
	
	def setPosition(self, v):
		self.mainPlayer.get_media_player().set_position(v)

	def setVolume(self, v):
		self.volume = int(v * 100)
		if self.mainPlayer != None:
			self.mainPlayer.get_media_player().audio_set_volume(self.volume)