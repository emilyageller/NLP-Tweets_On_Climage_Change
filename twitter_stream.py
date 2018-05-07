# This script connects to the streaming Twitter API and pulls Climate Change tweets into a MongoDB


import tweepy
import cnfg
import time
import json
from pymongo import MongoClient
import pymongo
from tqdm import tqdm



#override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        if status_code == 420 :
            #returning False in on_data disconnects the stream
            return False
    
def limit_handled(cursor):
    '''Returns next tweet. If a rate limit error occurs, wait for the appropriate amount of time before trying again.'''
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            print('\nRateLimitError.....sleeping....zzzzzzzzz.......\n')
            for i in tqdm(range(60)):
                time.sleep(5)
        except tweepy.TweepError as e:
            if e.message.split()[-1] == '429':
                print('\nTweepError 429....sleeping...zzzzzzzzz......\n')
                for i in tqdm(range(60)):
                    time.sleep(5)

                #print('\nTweepError 429....sleeping...zzzzzzzzz......\n')
                #time.sleep(15 * 60)
            else:
                print(e.message)

if __name__ == '__main__':


# Set up connection to Twitter API with tweepy
    config = cnfg.load(".twitter_config")
    auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
    auth.set_access_token(config['access_token'], config['access_token_secret'])
    api = tweepy.API(auth) 

# Set up connection to MongoDB on AWS
    client = pymongo.MongoClient()
    db = client.climatechange
    col = db.climate_tweets_stream


tweetCount = 0
print('Streaming tweets.')

# Stream tweets into MongoDB
for tweet in limit_handled(tweepy.Cursor(api.search, q ='#climatechange OR climate change OR #globalwarming OR global warming' , tweet_mode = 'extended').items()):
    col.insert(tweet._json)
    tweetCount += 1
    print(tweetCount)


print ("Downloaded {0} tweets, Saved to MongoDB ClimateChange".format(tweetCount))