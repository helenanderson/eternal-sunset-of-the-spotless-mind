from os import path

import requests
import tweepy

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

def most_recent_live_scope():
    tweets = twitter.search(q=QUERY, count=10)
    for tweet in tweets:
        print tweet.text
        for url in tweet.entities['urls']:
            expanded_url = url['expanded_url']
            if expanded_url.startswith('https://www.periscope.tv/w/'):
                scope_source = requests.get(expanded_url)
                if scope_is_live(scope_source):
                    return expanded_url
    for tweet in tweets:
        for url in tweet.entities['urls']:
            expanded_url = url['expanded_url']
            if expanded_url.startswith('https://www.periscope.tv/w/'):
                return expanded_url
    return "no scope found :("

def scope_is_live(scope_source):
    return 'isEnded&quot;:false' in scope_source
