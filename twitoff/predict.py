"""Prediction of Users based on Tweet embeddings."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from .models import User
from .twitter import BASILICA


def predict_user(user1_name, user2_name, user3_name, user4_name, tweet_text):
    """
    Determine and return which user is more likely to say a given Tweet.
    Example run: predict_user('austen', 'elonmusk', 'Lambda School rocks!')
    Returns 1 (corresponding to first user passed in) or 0 (second).
    """
    user_names = set((user1_name, user2_name, user3_name, user4_name))
    users = []
    user_embeddings = []
    for username in user_names:
        user = User.query.filter(User.name == username).one()
        users.append(user)
        user_embeddings.append(np.array([tweet.embedding for tweet in user.tweets]))

    embeddings = np.vstack(user_embeddings)
    ulabels = []
    for i, user in enumerate(users):
        ulabels.append(i * np.ones(len(user.tweets)))

    labels = np.concatenate(ulabels)

    log_reg = LogisticRegression().fit(embeddings, labels)
    # We've done our data science! Now to predict
    tweet_embedding = BASILICA.embed_sentence(tweet_text, model='twitter')
    return users[int(log_reg.predict(np.array(tweet_embedding).reshape(1, -1))[0])].name
