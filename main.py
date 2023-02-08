from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QCoreApplication, QStringListModel, QUrl, QObject, Signal, Property, Slot
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtGui import QFont, QFontDatabase
from app_logic import AppLogic
from os import sys
import utils

class Backend(QObject):

	def __init__(self, applogic, parent=None):
		QObject.__init__(self, parent)
		self.m_appLogic = applogic
		self.m_selectedIndex = -1

	@Slot()
	def onBackButtonClicked(self):
		self.m_appLogic.GoBack()
	@Slot()
	def onPlaylistsButtonClicked(self):
		self.m_appLogic.LoadPlaylists()
	@Slot()
	def onLibraryButtonClicked(self):
		self.m_appLogic.LoadArtists()
	@Slot(str)
	def onCreatePlaylistClicked(self, text):
		self.m_appLogic.CreatePlaylist(text)
	@Slot()
	def onPrevButtonClicked(self):
		self.m_appLogic.Prev()
	@Slot()
	def onPauseButtonClicked(self):
		self.m_appLogic.Pause()
	@Slot()
	def onNextButtonClicked(self):
		self.m_appLogic.Next()
	@Slot(int)
	def onListItemClicked(self, index):
		self.m_appLogic.OnItemSelected(index)
	@Slot(float)
	def onVolumeChanged(self, value):
		self.m_appLogic.SetVolume(value)
	@Slot(float)
	def onPositionChanged(self, value):
		self.m_appLogic.SetPosition(value)
	@Slot(str)
	def onSearchBarChanged(self, value):
		self.m_appLogic.OnSearch(value)
	@Property(int, notify=None)
	def state(self):
		return self.m_appLogic.state
	@Property(int, notify=None)
	def libState(self):
		return self.m_appLogic.libState
	@Property(int, notify=None)
	def playlistState(self):
		return self.m_appLogic.playlistState
	@Slot(int)
	def setSelectedIndex(self, index):
		self.m_selectedIndex = index
	@Slot()
	def copyMp3Url(self):
		self.m_appLogic.CopyMp3Url(self.m_selectedIndex)
	@Slot()
	def copyYoutubeUrl(self):
		self.m_appLogic.CopyYoutubeUrl(self.m_selectedIndex)
	@Slot()
	def addToQueue(self):
		self.m_appLogic.AddToQueue(self.m_selectedIndex)
	@Slot()
	def getPlaylists(self):
		self.m_appLogic.GetPlaylists()
	@Slot(int)
	def addToPlaylist(self, index):
		self.m_appLogic.AddToPlaylist(index, self.m_selectedIndex)

if __name__ == '__main__':
	sys.argv += ['--style', 'material']

	defaultVolume = utils.config["defaultVolume"] if "defaultVolume" in utils.config.keys() else 0.5

	QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
	app = QApplication(sys.argv)

	fdb = QFontDatabase()
	fdb.addApplicationFont("fonts/FiraSans-Regular.ttf")
	appFont = QFont("Fira Sans")
	app.setFont(appFont)

	QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
	engine = QQmlApplicationEngine()

	# Expose the list to the Qml code
	listViewModel = QStringListModel()
	playlistListViewModel = QStringListModel()

	appLogic = AppLogic(listViewModel, playlistListViewModel, defaultVolume)
	backend = Backend(appLogic)

	appLogic.LoadArtists()

	engine.rootContext().setContextProperty("appDirPath", __file__[:__file__.rfind('\\')] + "/")
	engine.rootContext().setContextProperty("listViewModel", listViewModel)
	engine.rootContext().setContextProperty("playlistListViewModel", playlistListViewModel)
	engine.rootContext().setContextProperty("backend", backend)

	with open("view.qml", 'r') as qmlFile:
		qmlCode = qmlFile.read()
	qmlCode = qmlCode.replace("__DEFAULT_VOLUME__", str(defaultVolume))

	engine.loadData(qmlCode.encode('utf-8'))

	sys.exit(app.exec_())
