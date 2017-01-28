from flask import Flask, Markup
from threading import Timer
from fetch_scope import most_recent_scope, scope_is_live
from flask import render_template, jsonify
import requests
import os

app = Flask(__name__)

stylingscript = "<script type='text/javascript'> var hideTwitterAttempts = 0; function hideTwitterBoxElements() { setTimeout( function() { $('#tweetembeddiv /deep/ .Tweet-header, #tweetembeddiv /deep/ .Tweet-text, #tweetembeddiv /deep/ .Tweet-metadata, #tweetembeddiv /deep/ .Tweet-actions, #tweetembeddiv /deep/ .SummaryCard-content').attr('style', 'display:none !important;'); $('#tweetembeddiv /deep/ .EmbeddedTweet').attr('style', 'border:0px !important;'); $('#tweetembeddiv /deep/ .EmbeddedTweet-tweet').attr('style', 'padding: 20px;'); $('#tweetembeddiv /deep/ .Tweet-body, #tweetembeddiv /deep/ .Tweet-card').attr('style', 'margin:0px !important;');$('#tweetembeddiv /deep/ .TwitterCardsGrid-col--spacerBottom').attr('style', 'margin:0px !important;'); hideTwitterAttempts++; if ( hideTwitterAttempts < 3 ) { hideTwitterBoxElements(); } }, 1500); } hideTwitterBoxElements(); </script>"

# There's probably a better way to do this where we don't have to keep track of both of these things globally, but for now...
current_scopes = {
	'sunrise': None,
	'sunset': None
}
INTERVAL = 60.0

def constructEmbedHTML(key):
	global current_scopes
	global stylingscript
	current_tweet = current_scopes[key][0]
	embed_url = 'https://api.twitter.com/1.1/statuses/oembed.json?id=' + str(current_tweet.id)
	oembed = requests.get(embed_url).json()
	return oembed['html'] + stylingscript

@app.route('/_sets')
def sets():
	tweetHtml = constructEmbedHTML('sunset')
	print tweetHtml
	return jsonify(result=tweetHtml)

@app.route('/_rises')
def rises():
	tweetHtml = constructEmbedHTML('sunrise')
	print tweetHtml
	return jsonify(result=tweetHtml)

@app.route("/")
def home():
	global current_scopes
	initial_tweet_html = Markup(constructEmbedHTML('sunrise'))
	return render_template('home.html', scope=initial_tweet_html)

def updateScopes():
	global current_scopes

	for key in current_scopes:
		# If the current scope is still live, don't bother changing it
		current_scope = current_scopes[key]
		if current_scope is None or not scope_is_live(requests.get(current_scope[1])):
			current_scopes[key] = most_recent_scope(key)

	timer = Timer(INTERVAL, updateScopes)
	timer.start()

if __name__ == "__main__":
	updateScopes()
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
