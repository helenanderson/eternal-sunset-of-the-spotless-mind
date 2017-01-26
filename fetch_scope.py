from os import path
import os
import requests
import tweepy
import datetime
import re

# Returns (consumer_key, consumer_secret)
# def load_twitter_secrets():
#     twitter_filename = path.join('secrets', 'twitter.txt')
#     with open(twitter_filename, 'r') as twitter_file:
#         return twitter_file.read().strip().split('\n')

def load_auth():
    # consumer_key, consumer_secret = load_twitter_secrets()
    return tweepy.AppAuthHandler(os.environ['TWITTER_KEY'], os.environ['TWITTER_SECRET'])

twitter_auth = load_auth()
twitter = tweepy.API(twitter_auth)

# Returns tweet object
def most_recent_scope(query):
    all_scopes = []
    tweets = twitter.search(q='periscope ' + query)
    for tweet in tweets:
        print tweet.text
        print "\n"
        for url in tweet.entities['urls']:
            expanded_url = url['expanded_url']
            print expanded_url
            if expanded_url.startswith('https://www.periscope.tv/w/'):
                response = requests.get(expanded_url)
                scope_info = (expanded_url, start_time(response), scope_is_live(response))
                if scope_info not in all_scopes:
                    all_scopes.append(scope_info)
    sorted_scopes = sorted(all_scopes, key=lambda x: x[1], reverse=True)
    print sorted_scopes
    live_scopes = [x for x in sorted_scopes if x[2] is True]
    if len(live_scopes) > 0:
        return live_scopes[0][0]
    elif len(sorted_scopes) > 0:
        return sorted_scopes[0][0]
    else:
        return None


def scope_is_live(response):
    return 'isEnded&quot;:false' in response.text

def start_time(response):
    m = re.search(r'start&quot;:&quot;((\d\d\d\d)-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d))', response.text)
    return m.group(1)

def scope_in_timeframe(tweet, hours):
    return datetime.datetime.now() - tweet.created_at < datetime.timedelta(hours = hours)
