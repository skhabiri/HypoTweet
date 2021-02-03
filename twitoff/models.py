"""SQLAlchemy models and utility functions for TwitOff."""
from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class User(DB.Model):
    """A class/model for Twitter users"""
    id = DB.Column(DB.BigInteger, primary_key=True)
    name = DB.Column(DB.String(15), nullable=False)
    # Tweet IDs are ordinal ints, so can be used to fetch only more recent ones
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return '-User:{}, id:{}, tweet length:{}-'.format(self.name, self.id, len(self.tweets))


class Tweet(DB.Model):
    """Tweet text class/data model.
    instances of User() will be entries to a sql table named 'user'"""
    id = DB.Column(DB.BigInteger, primary_key=True)
    
    # Unicode allows for emojis, max tweet length is 270
    text = DB.Column(DB.Unicode(300))  # Allows for text + links
    # The embedding type is masked by using the PickleType. Letting
    # sqlalchemy to take care of it
    embedding = DB.Column(DB.PickleType, nullable=False)
 
    # User is the class name. 'user.id' refers to column "id" of user sql table.
    # python class is capitalized, and sql convention for variables is lower case.
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    
    # The "user" field in Tweet class is the User object
    # Backreference is used to avoid explicit join as the model object shows up as 
    # a field in another model. 
    # Here a field named "tweets" is added to the User model as a Tweet() object.
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
        return '-Tweet:{}, id:{}, user_id:{}, user name:{}-'.format(
            self.text, self.id, self.user_id, self.user)
