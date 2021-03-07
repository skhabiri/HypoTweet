"""Prediction of Users based on Tweet embeddings."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from .models import User
from .twitter import BASILICA 
# from .twitter import nlp 


def predict_user(user1_name, user2_name, user3_name, user4_name, tweet_text):
    """
    Determine and return which user is more likely to say a given Tweet.
    Example run: predict_user('austen', 'elonmusk', 'Lambda School rocks!')
    Returns 0 (corresponding to the first user passed on).
    """
    user_names = set((user1_name, user2_name, user3_name, user4_name))
    
    # Create X for sklearn model
    users = []
    user_embeddings = []
    for username in user_names:
        user = User.query.filter(User.name == username).one()
        users.append(user)
        user_embeddings.append(np.array([tweet.embedding for tweet in user.tweets]))

    embeddings = np.vstack(user_embeddings)

    # create target labels y
    ulabels = []
    for i, user in enumerate(users):
        ulabels.append(i * np.ones(len(user.tweets)))

    labels = np.concatenate(ulabels)

    log_reg = LogisticRegression().fit(embeddings, labels)

    tweet_embedding = BASILICA.embed_sentence(tweet_text, model='twitter')
    # tweet_embedding = nlp(tweet_text).vector

    # predict returns float
    return users[int(log_reg.predict(np.array(tweet_embedding).reshape(1, -1))[0])].name
