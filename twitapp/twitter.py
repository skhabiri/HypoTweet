"""
Retrieve Tweets, 
generate embeddings, 
and persist in the database.
"""

from os import getenv
# import basilica
import spacy

import tweepy
# relative path to the module name
from .models import DB, Tweet, User


TWITTER_USERS = ['zerohedge', 'nasa', 'espn', 'AmerMedicalAssn']

TWITTER_API_KEY = getenv('TWITTER_API_KEY')
TWITTER_API_KEY_SECRET = getenv('TWITTER_API_KEY_SECRET')
TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
TWITTER = tweepy.API(TWITTER_AUTH)
# BASILICA = basilica.Connection(getenv('BASILICA_KEY'))

nlp = spacy.load("en_core_web_sm")

def add_or_update_user(username):
    """pull a user from twitter if not already in db
    and update its Tweets, error if not a Twitter user."""
    try:
        twitter_user = TWITTER.get_user(username)
        # either in db or not
        # .get(): Return an instance based on the given primary key identifier
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id, name=username))

        # in sqlalchemy if db_user.id already exists it overwrites it. 
        # But won't duplicate it, as id is unique.
        DB.session.add(db_user)
        
        # Lets get the tweets - focusing on primary (not retweet/reply)
        # tweets gets updated even for existing users in db 
        tweets = twitter_user.timeline(
            count=200, exclude_replies=True, include_rts=False,
            tweet_mode='extended', since_id=db_user.newest_tweet_id
        )
        # if any new tweet since the last one, update the pointer
        if tweets:
            # tweets[0] is the latest tweet that api returns
            db_user.newest_tweet_id = tweets[0].id
        for tweet in tweets:
            # embedding = BASILICA.embed_sentence(tweet.full_text, model='twitter')
            embedding = nlp(tweet.full_text).vector
            
            db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:300], embedding=embedding)
            
            # we can either manually append it or 
            # when added to db the two models User and Tweet implicitely join
            # We don't need to add db_user to the session. 
            # Because User object is inside db_tweet already.
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
            
    except Exception as e:
        print('Error processing {}: {}'.format(username, e))
        raise e
    
    # executed if exception not raised
    else:
        DB.session.commit()


def insert_example_users():
    """Example data to play with."""
    for user in TWITTER_USERS:
        add_or_update_user(user)
