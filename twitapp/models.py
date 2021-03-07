"""SQLAlchemy models and utility functions for twitapp."""
from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class User(DB.Model):
    """A data model for Twitter users. 
    - instances of User() will be entries to a table named 'user' in DB database
    - Each entry include an `id`, `name`, and `newesr_tweet_id`
    """
    id = DB.Column(DB.BigInteger, primary_key=True)
    name = DB.Column(DB.String(15), nullable=False)
    # Tweet IDs are ordinal ints, so can be used to fetch only more recent ones
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return '-User:{}, id:{}, tweet length:{}-'.format(self.name, self.id, len(self.tweets))


class Tweet(DB.Model):
    """`Tweet` is a data model for `tweet` table entries.
   """
    id = DB.Column(DB.BigInteger, primary_key=True)
    
    # Unicode allows for emojis, max tweet length is 270. 
    # A little longer length to have complete url links as well
    text = DB.Column(DB.Unicode(300))  # Allows for text + links
    
    # The embedding type is masked by using the multi purpose PickleType. 
    # Letting sqlalchemy to take care of it
    embedding = DB.Column(DB.PickleType, nullable=False)
 
    # `User` is the class name. 'user.id' refers to column "id" column of the `user` table in `DB` database.
    # python class is capitalized, and sql convention for variables is lower case. 
    # so table name is lower case and data model starts upper case.
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    
    # The field with arbitrary name of "user" in Tweet class is back referenced to the User object
    # Backreference is used to avoid explicit join.
    # Backrefrence allows the entire model object to show up as another field in another data model. 
    # A field arbitrarily name "tweets" is added to the `User` data model as a back reference to the Tweet() object.
    # Backrefrenced is connected using Foreign key
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
        return '-Tweet:{}, id:{}, user_id:{}, user object:{}-'.format(
            self.text, self.id, self.user_id, self.user)
