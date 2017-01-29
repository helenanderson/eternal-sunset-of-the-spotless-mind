from flask import Flask, Markup
from threading import Timer
from fetch_scope import most_recent_scopes, scope_is_live
from flask import render_template, jsonify
import requests
import os

app = Flask(__name__)

stylingscript = "<script type='text/javascript'> $('#tweetembeddiv').hide(); var hideTwitterAttempts = 0; function hideTwitterBoxElements() { setTimeout( function() { $('#tweetembeddiv /deep/ .Tweet-header, #tweetembeddiv /deep/ .Tweet-text, #tweetembeddiv /deep/ .Tweet-metadata, #tweetembeddiv /deep/ .Tweet-actions, #tweetembeddiv /deep/ .SummaryCard-content, #tweetembeddiv /deep/ .EmbeddedTweet-ancestor').attr('style', 'display:none !important;'); $('#tweetembeddiv /deep/ .EmbeddedTweet').attr('style', 'border:0px !important;'); $('#tweetembeddiv /deep/ .EmbeddedTweet-tweet').attr('style', 'padding: 20px;'); $('#tweetembeddiv /deep/ .Tweet-body, #tweetembeddiv /deep/ .Tweet-card').attr('style', 'margin:0px !important;');$('#tweetembeddiv /deep/ .TwitterCardsGrid-col--spacerBottom').attr('style', 'margin:0px !important;'); if( !$('#tweetembeddiv /deep/ .Tweet-card').length) {$('#refresh').trigger('click');} else {$('#tweetembeddiv').show();}}, 1500); } hideTwitterBoxElements(); </script>"

# There's probably a better way to do this where we don't have to keep track of both of these things globally, but for now...
current_scopes = {
	'sunrise': [],
	'sunset': []
}
current_sun_direction = "sunrise"
INTERVAL = 30.0

error_message = "<div style='width:30%;margin-top:10%;text-align:center;'><h1 style='color:#DB4F4F;'>SORRY, WE COULDN'T FIND A " + current_sun_direction.upper() + " FOR YOU!</h1><h1> TRY REFRESHING, OR CHECK BACK LATER.</h1></div>"

def constructEmbedHTML(key, scope):
	global current_scopes
	global stylingscript
	global error_message
	if not scope:
		return error_message
	current_tweet = scope[0]
	embed_url = 'https://api.twitter.com/1.1/statuses/oembed.json?id=' + str(current_tweet.id)
	oembed = requests.get(embed_url).json()
	# mark that we've seen this Scope
	current_scopes[key][current_scopes[key].index(scope)][4] = True
	return oembed['html'] + stylingscript

def findFirstUnseen(sunDirection):
	global current_scopes
	unseen = [scope for scope in current_scopes[sunDirection] if scope[4] is False]
	if len(unseen) is 0:
		for scope in current_scopes[sunDirection]:
			scope[4] = False
		return current_scopes[sunDirection][0]
	return unseen[0]

@app.route('/_refreshsunrise')
def refreshsunrise():
	first_unseen = findFirstUnseen('sunrise')
	tweetHtml = constructEmbedHTML('sunrise', first_unseen)
	return jsonify(result=tweetHtml)

@app.route('/_refreshsunset')
def refreshsunset():
	first_unseen = findFirstUnseen('sunset')
	tweetHtml = constructEmbedHTML('sunset', first_unseen)
	return jsonify(result=tweetHtml)

@app.route('/_sunset')
def sunset():
	global current_sun_direction
	tweetHtml = constructEmbedHTML('sunset', current_scopes['sunset'][0])
	print tweetHtml
	current_sun_direction = "sunset"
	return jsonify(result=tweetHtml)

@app.route('/_sunrise')
def sunrise():
	global current_sun_direction
	tweetHtml = constructEmbedHTML('sunrise', current_scopes['sunrise'][0])
	current_sun_direction = "sunrise"
	return jsonify(result=tweetHtml)

@app.route("/")
def home():
	global current_scopes
	global current_sun_direction
	initial_tweet_html = Markup(constructEmbedHTML('sunrise', current_scopes['sunrise'][0]))
	return render_template('home.html', scope=initial_tweet_html)

def updateScopes():
	global current_scopes

	for key in current_scopes:
		current_scopes[key] = most_recent_scopes(key, current_scopes[key])

	timer = Timer(INTERVAL, updateScopes)
	timer.start()

if __name__ == "__main__":
	updateScopes()
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
