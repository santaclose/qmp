import flask
import threading
import json
# import player_mpv as player_module

app = flask.Flask(__name__)

@app.route("/")
def hello_world():
	return "asdf"

player = None

@app.route("/play", methods=['POST'])
def play():
	global player
	json_object = flask.request.json
	player.play(json_object['playlist'], json_object['index'])
	return "", 200

@app.route("/next", methods=['POST'])
def next():
	global player
	player.next()
	return "", 200

@app.route("/prev", methods=['POST'])
def prev():
	global player
	player.previous()
	return "", 200

@app.route("/pause", methods=['POST'])
def pause():
	global player
	player.pause()
	return "", 200

@app.route("/add", methods=['POST'])
def add():
	global player
	json_object = flask.request.json
	player.addToQueue(json_object['url'])
	return "", 200

@app.route("/seek", methods=['POST'])
def seek():
	global player
	json_object = flask.request.json
	player.setPosition(json_object['value'])
	return "", 200

@app.route("/volume", methods=['POST', 'GET'])
def volume():
	global player
	if flask.request.method == 'GET':
		return json.dumps({"value": player.getVolume()})
	else:
		json_object = flask.request.json
		player.setVolume(json_object['value'])
		return "", 200

def _run(port):
	app.run(host='0.0.0.0', port=port)

def run(player_in, port=656):
	global player
	player = player_in
	x = threading.Thread(target=_run, args=(port,))
	x.start()

if __name__ == '__main__':
	import player_mpv as player_module
	player = player_module.Player()
	run(player)