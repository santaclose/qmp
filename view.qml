import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3
import QtQuick.Controls.Material 2.1

ApplicationWindow {

	title: "qmp"
	visible: true
	width: 360
	height: 650
	
	Material.theme: Material.Dark

	menuBar: ToolBar {
		RowLayout {
			width: parent.width

			ToolButton {
				Layout.alignment: Qt.AlignLeft
				text: "\uE72B"
				onClicked: {
					backend.onBackButtonClicked()
					searchTextField.text = ""
				}
			}

			TextField {
				id: searchTextField
				placeholderText: qsTr("Search")
				Layout.alignment: Qt.AlignCenter
				onTextChanged: backend.onSearchBarChanged(text)
			}

			ToolButton {
				Layout.alignment: Qt.AlignRight
				text: "\uE767"
				onClicked: {
					volumeMenu.open()
				}
			}

			ToolButton {
				Layout.alignment: Qt.AlignRight
				text: "\uE700"
				onClicked: {
					appMenu.open()
				}
			}
		}
	}
	
	ListView {
		id: listView
		anchors.fill: parent
		topMargin: 16
		leftMargin: 8
		bottomMargin: 16
		rightMargin: 8
		spacing: 4
		model: listViewModel
		delegate: ItemDelegate {
			text: model.display
			width: listView.width - listView.leftMargin - listView.rightMargin
			property int indexOfThisDelegate: index
			MouseArea {
				anchors.fill: parent
				acceptedButtons: Qt.LeftButton | Qt.RightButton
				onClicked:
				{
					if (mouse.button == Qt.RightButton)
					{
						if (backend.state == 0 && backend.libState == 2)
						{
							backend.setSelectedIndex(index)
							songContextMenu.open()
						}
					}
					else
						backend.onListItemClicked(index)
				}
			}
		}
	}
 
	footer: ToolBar {
		RowLayout {
			width: parent.width
			ToolButton {
				Layout.alignment: Qt.AlignLeft
				text: "\uE892"
				onClicked: backend.onPrevButtonClicked()
			}
			ToolButton {
				Layout.alignment: Qt.AlignLeft
				text: "\uEDB4"
				onClicked: backend.onPauseButtonClicked()
			}
			ToolButton {
				Layout.alignment: Qt.AlignLeft
				text: "\uE893"
				onClicked: backend.onNextButtonClicked()
			}
			Slider {
				value: 0.0
				onMoved: backend.onPositionChanged(value)
			}
		}
	}

	Menu {
		id: appMenu
		x: parent.width - width
		MenuItem {
			text: "Library"
			onClicked: backend.onLibraryButtonClicked()
		}
		MenuItem {
			text: "Playlists"
			onClicked: backend.onPlaylistsButtonClicked()
		}
	}

	Menu {
		id: volumeMenu
		x: parent.width - width
		Slider {
			value: 0.5
			onMoved: backend.onVolumeChanged(value)
		}
	}

	Menu {
		id: songContextMenu
		anchors.centerIn: parent
		
		MenuItem {
			text: "Copy mp3 url"
			onClicked: backend.copyMp3Url()
		}
		MenuItem {
			text: "Add to playlist"
			onClicked:
			{
				backend.getPlaylists()
				playlistSelectionMenu.open()
			}
		}
	}

	Menu {
		id: playlistSelectionMenu
		anchors.centerIn: parent
		ListView {
			id: playlistListView
			anchors.fill: parent
			model: playlistListViewModel
			delegate: ItemDelegate {
				text: model.display
				width: listView.width - listView.leftMargin - listView.rightMargin
				property int indexOfThisDelegate: index
				onClicked:
				{
					backend.addToPlaylist(index)
					playlistSelectionMenu.close()
				}
			}
		}
	}
}