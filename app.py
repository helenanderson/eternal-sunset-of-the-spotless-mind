from flask import Flask
from threading import Timer
from fetch_scope import most_recent_live_scope, scope_is_live
import requests

app = Flask(__name__)

# There's probably a better way to do this where we don't have to keep track of both of these things globally, but for now...
current_tweet = None
current_scope = None
INTERVAL = 15.0

@app.route("/")
def home():
	return constructEmbedHTML()

def constructEmbedHTML():
	global current_tweet
	embed_url = 'https://api.twitter.com/1.1/statuses/oembed.json?id=' + str(current_tweet.id)
	oembed = requests.get(embed_url).json()
	return oembed['html']

def updateScope():	
	global current_scope 
	global current_tweet

	# If the current scope is still live, don't bother changing it
	if current_scope is None or not scope_is_live(current_scope):
		current_tweet, current_scope = most_recent_live_scope()

	timer = Timer(INTERVAL, updateScope)
	timer.start()

if __name__ == "__main__":
	updateScope()
	app.run()