"""Main app/routing file for TwitOff."""
from os import getenv

# different from requests library
from flask import Flask, render_template, request
# request: passes variable from html POST to .py
# render_template: passes variable from .py to jinja2 in html

# import from .py files comes with relative path "."
from .models import DB, User
from .predict import predict_user
from .twitter import add_or_update_user, insert_example_users


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)   
    
    # telling app where to connect to the database
    # Saves the database into db.sqlite3 file. /// is relative path
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the db server and connect it to the application
    DB.init_app(app)

    # create main route with decorator, Home page
    @app.route('/')
    def root():
        """load all the users from db onto the home page"""
        ## static return
        # return 'Hello, TwitOff!'

        # return parameters are passed to the html template through jinja2 syntax {}
        return render_template('base.html', title='Home',
                               users=User.query.all())

    # We can have two decorators with one function
    # Post means the user posts some information 'user_name'
    # Get means the user gets some information back, <name>
    # In GET method, <name> is a variable that is passed from url to the decorator function
    # request.value['variable'] fetches the posted variable from the html.
    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        """
        /user: call api to get a new user and its tweets and render the user name and
        its tweets on the page
        
        /user/<name>: get the existing user's tweets from db and render the user name and
        its tweets on the page."""

        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = "User {} successfully added!".format(name)
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = "Error adding {}: {}".format(name, e)
            tweets = []
        return render_template('user.html', title=name, tweets=tweets,
                               message=message)

    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        """ user1, user2 ,... are variables in base.html that are "selected" from a list of "options"
        tweet_text is  the hypothetical tweet passed from html to python with request.values
        we get the user names of the selected users. Then run a logistic regression on the embedded
        tweets of those users that exist in db, and predict which one the hypothetical tweet belongs to.
        """

        # depending on which user is selected first on the form user1 in html might be assigned
        # Regardless of that we would not need sort!
        user1, user2, user3, user4 = sorted([request.values['user1'],
                                     request.values['user2'],
                                     request.values['user3'],
                                     request.values['user4'],
                                     ])
        # for debugging
        print("\n\nuser1:{}, user4:{}\n\n".format(user1, user4))
        
        if user1 == user2 == user3 == user4:
            message = 'Select two or more different users!'
        else:
            user_name = predict_user(user1, user2, user3, user4,
                                      request.values['tweet_text'])
            message = '"{}" is more likely to be said by {}'.format(
                request.values['tweet_text'], user_name)
        return render_template('prediction.html', title='Prediction',
                               message=message)

    # create another route
    @app.route('/update')
    def update():
        """call twitter api to fetch tweets and user info of a selected number of users
        and reload the app users with all the users in db including the updated ones"""
        insert_example_users()  
        return render_template('base.html', title='Users updated!',
                               users=User.query.all())

    @app.route('/reset')
    def reset():
        """ reset the db"""
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='Reset database!')

    return app
