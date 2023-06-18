import os # add dll folder to path
os.environ["PATH"] = os.path.join(os.path.dirname(__file__), "mpv") + os.pathsep + os.environ["PATH"]
import mpv
import time

class Player:
	
	def __init__(self):
		self.player = mpv.MPV()

	def play(self, playlist, index):
		self.player.stop()
		[self.player.playlist_append(url) for url in playlist]
		self.player.playlist_play_index(index)
		self.player.pause = False

	def next(self):
		self.player.playlist_next()

	def pause(self):
		self.player.pause = not self.player.pause
	
	def previous(self):
		self.player.playlist_prev()
	
	def stop(self):
		self.player.stop()
	
	def setPosition(self, v): # v from 0 to 1
		self.player.time_pos = self.player.duration * v

	def setVolume(self, v): # v from 0 to 1
		self.player.volume = v * 100

	def getVolume(self):
		return self.player.volume / 100.0

	def addToQueue(self, song):
		self.player.playlist_append(song)