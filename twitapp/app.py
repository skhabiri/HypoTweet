"""Main app/routing file for twitapp."""
from os import getenv

# different from requests library
from flask import Flask, render_template, request
# request: passes variable from html POST to .py
# render_template: passes variable from .py to jinja2 used in html

# import from .py files comes with relative path "."
from .models import DB, User
from .predict import predict_user
from .twitter import add_or_update_user, insert_example_users


def create_app():
    """Create and configure an instance of the Flask application.
    1. instantiate the flask app
    2. connect the database
    3. create the routes
    """
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

    # It;s possible to have two decorators with only one function
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

        It needs atleast two users to be selected. 
        """

        # Might need sort depending on html behavior on how to pass it
        count = 0
        username, filler = [None] * 4, None

        for i in range(4):
            name = f'user{i+1}'

            try:
                username[i] = request.values[name]
                count += 1
            except Exception as e:
                pass
            
            # only if exception hasn't occured. Though not needed here
            else:
                filler = username[i]
                continue
            # always enter this
            finally:
                print("*"*20, username[i])
                continue
    
        
        # Not-selected users are filled with one of the selected ones
        if count != 4:
            for i in range(4):
                if not username[i]:
                    username[i] = filler
        

        if all(v is None for v in [username[i] for i in range(4)]) or (username[0] == username[1] == username[2] == username[3]):
            message = "Please select two or more different users"
            return render_template('prediction.html', title='Prediction', message=message)


        try:
            hypotext = request.values['tweet_text']
        
        except Exception as e:
            message = "Please enter a hypothetical tweet"
            return render_template('prediction.html', title='Prediction', message=message)
        
        if len(hypotext) == 0:
            message = "Please enter a hypothetical tweet"
            return render_template('prediction.html', title='Prediction', message=message)


        user_name = predict_user(username[0], username[1], username[2], username[3], hypotext)
        message = '"{}" is more likely to be said by {}'.format(hypotext, user_name)
        
        return render_template('prediction.html', title='Prediction', message=message)

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
