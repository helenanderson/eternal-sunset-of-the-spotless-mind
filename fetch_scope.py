from os import path

import requests
import tweepy
import datetime

QUERY = 'periscope sunset'

# Returns (consumer_key, consumer_secret)
def load_twitter_secrets():
    twitter_filename = path.join('secrets', 'twitter.txt')
    with open(twitter_filename, 'r') as twitter_file:
        return twitter_file.read().strip().split('\n')

def load_auth():
    consumer_key, consumer_secret = load_twitter_secrets()
    return tweepy.AppAuthHandler(consumer_key, consumer_secret)

twitter_auth = load_auth()
twitter = tweepy.API(twitter_auth)

# Returns tweet object
def most_recent_live_scope():
    tweets = twitter.search(q=QUERY)
    for tweet in tweets:
        print tweet.text
        for url in tweet.entities['urls']:
            expanded_url = url['expanded_url']
            if expanded_url.startswith('https://www.periscope.tv/w/'):
                if scope_is_live(expanded_url):
                    return tweet, expanded_url
    for tweet in tweets:
        for url in tweet.entities['urls']:
            expanded_url = url['expanded_url']
            if expanded_url.startswith('https://www.periscope.tv/w/'):
                return tweet, expanded_url
    return "no scope found :("

def scope_is_live(expanded_url):
    return 'isEnded&quot;:false' in requests.get(expanded_url)

def scope_in_timeframe(tweet, hours):
    return datetime.datetime.now() - tweet.created_at < datetime.timedelta(hours = hours)
