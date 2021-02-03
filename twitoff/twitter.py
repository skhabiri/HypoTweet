"""Retrieve Tweets, embeddings, and persist in the database."""
from os import getenv
import basilica
import tweepy
from .models import DB, Tweet, User


TWITTER_USERS = ['austen', 'elonmusk', 'KingJames', 'kylegriffin1']

TWITTER_API_KEY = getenv('TWITTER_API_KEY')
TWITTER_API_KEY_SECRET = getenv('TWITTER_API_KEY_SECRET')
TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA = basilica.Connection(getenv('BASILICA_KEY'))


def add_or_update_user(username):
    """pull a user fromt witter if not already in db
    and update its Tweets, error if not a Twitter user."""
    try:
        twitter_user = TWITTER.get_user(username)
        # either in db or not
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
            embedding = BASILICA.embed_sentence(tweet.full_text,
                                                model='twitter')
            db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:300],
                             embedding=embedding)
            # we can either manually append it or 
            # when added to db the two models User, Tweet implicitely join
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
            
    except Exception as e:
        print('Error processing {}: {}'.format(username, e))
        raise e
    else:
        DB.session.commit()


def insert_example_users():
    """Example data to play with."""
    for user in TWITTER_USERS:
        add_or_update_user(user)
