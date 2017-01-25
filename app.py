from flask import Flask
from threading import Timer
from fetch_scope import most_recent_scope, scope_is_live
from flask import render_template, jsonify
import requests

app = Flask(__name__)

# There's probably a better way to do this where we don't have to keep track of both of these things globally, but for now...
current_scopes = {
	'sunrise': None,
	'sunset': None
}
INTERVAL = 60.0

@app.route('/_sets')
def sets():
	return jsonify(result=current_scopes['sunset'])

@app.route('/_rises')
def rises():
	return jsonify(result=current_scopes['sunrise'])

@app.route("/")
def home():
	global current_scopes
	return render_template('home.html', scope=current_scopes['sunrise'])

def updateScopes():
	global current_scopes

	for key in current_scopes:
		# If the current scope is still live, don't bother changing it
		current_scope = current_scopes[key]
		if current_scope is None or not scope_is_live(requests.get(current_scope)):
			current_scopes[key] = most_recent_scope(key)

	timer = Timer(INTERVAL, updateScopes)
	timer.start()

if __name__ == "__main__":
	updateScopes()
	app.run()
