from flask import Flask
from threading import Timer
from fetch_scope import most_recent_live_scope

app = Flask(__name__)
current_scope = None
INTERVAL = 15.0

@app.route("/")
def home():
	global current_scope
	return current_scope

def updateScope():	
	global current_scope 
	current_scope = most_recent_live_scope()

	timer = Timer(INTERVAL, updateScope)
	timer.start()

if __name__ == "__main__":
	updateScope()
	app.run()