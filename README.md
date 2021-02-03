# TwitOff
A web application that takes up to 4 users. It connects to Twitter API to pull the user information including user id, latest tweets, tweet id. For a hypothetical tweet it predicts which of the users might have said that.
Once a tweet is entered it fits a multiclass logistic regression on the selected users' tweets which have previousely been embeded with basilica and stored in database. Then it connects to basilica API to embed the hypothetical tweet into 670 vectors and then runs a prediction on that to identify which user might have said that.
___

# Productization-and-Cloud-u3s3
Web Application Development with Flask-u3s3m1:
* Frontend-backend-database:
   * Frontend is presentation and interactions. Frontend code runs on the client machine. It defines what is rendered on the client side, and interacts with the client.
   * Backend is the business logic where data is processed and exchanged with the frontend. For scaling we might have multiple servers in the backend that are stateless, receiving requests and responding. They are all connected to the same database server.
   * Database is the persistence and where the data is stored and persisted. 
Flask is a python web application framework. As an example, Plotly dash is built on Flask.
steps to follow:
* Create twitoff repository
* git clone the repo on your local machine
* create virtual environment `pipenv --python 3.6`
* pipenv shell
* pipenv install flask jinja2 flask-sqlalchemy
* Create a basic app with hello.py
   * from flask import Flask
   * app = Flask(__name__)
   * @app.route(‘/’)
   * def hello_world():
      * return ‘Hello, World!’
* FLASK_APP=hello.py flask run
   * This is a minimal flask app
* Now create a directory for app with __init__.py file as the point of entry for the app
* create app.py as the main app/routing file. By default FLASK looks for that.
* At base directory enter `FLASK_APP=twitterclf:APP flask run` to run the app locally.
   * It would also run without the name of the application, APP, `FLASK_APP=twitterclf flask run`, or going to application directory twitterclf\> and enter `flask run`
* Instead of static return for a route we can return render_template(html file). The {} in html is jinja2 syntax allows passing parameters to flask.render_template(). flask app looks for templates directory under app directory.
* create model.py under app directory for sqlalchemy. sqlalchemy is used to connect to a sql database without having to write sql queries. It is used mostly for web applications. Here we create classes to define data model and use the lower case of the class as sql table name. entries of the table are instances of the data model class.
   * User.id, User.name, Tweet.id, Tweet.text, Tweet.user_id
* we can get a flask configured shell in the context of our app with `FLASK_APP=twitterclf:APP flask shell`. This is useful for debugging.
   * from twitterclf.models import User, Tweet, DB
   * austen = User(id=1, name=’austen’)
   * austen
   * elon = User(id=2, name=’elonmusk’)
   * tweet1 =Tweet(id=101, text=”lambda rocks!”, user_id=1
   * DB.session.add(austen)
   * DB.session.add(elon)
   * resultt = Tweet.query.all()
   * resultu = User.query.all()
   * resultu[0].tweets[0].text
   * resultt.user.name
___
Consuming-data-from-an-api-u3s3m2:
Instead of having a monolithic app with all the front-end, database, and backend as one service, the new approach is to have multiple micro services where each server provides a specific service.
### Connect to Twitter API: 
* get access to twitter developer. Then create a standalone app to get a API key, which is an identifier for the app and API secret key which is the password. 
* install tweepy locally to connect to the twitter api
* TWITTER_API_KEY = ‘<api_key>’
* TWITTER_API_SECRET_KEY = ‘’<api_secret_key>’
* auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
* twitter = tweepy.API(auth)
* user = ‘KingJames’
* twitter_user = twitter.get_user(user)
* twitter_user
* dir(twitter_user)
* twitter_user.id, twitter_user.name, …
* tweets = twitter_user.timeline(count=200, exclude_replies=True, include_rts=False, tweet_mode=’Extended’)
* len(tweets), tweets[0].text
* create a module in the app named twitter.py to add the twitter api code.
* We code a function to pull a twitter user from api based on the twitter handle. Then add that to User and Tweet models in the database with id and name and append all the tweets. Here is how to test it in flask shell:
   * FLASK_APP=twitoff flask shell
   * from twitoff.twitter import add_or_update_user
   * from twitoff.models import User, Tweet, DB
   * User.query.all()
   * add_or_update_user(‘kingjames’)
   * User.query.all()
   * user1 = User.query.get(1)        # get(id) this gets austen User
   * user2 = User.query.filter(User.name==’kingjames’).one()        #in case there are multiple matches return only one
   * len(user2.tweets)
   * user2.tweets[0]
* To process the tweets we use Basilica embedding. Go to basilica and get the API key for your application.
* create a basilica object b = basilica.Connection(basilica_key)
* tweet_text = user2.tweets[0].text
* embedding = b.embed_sentence(tweet_text, model=’twitter’)
* len(embedding)
* Can use `git diff twitoff/models.py` to see the recent changes
___
Adding Data Science to a Web Application-u3s3m3:
Each tweet is embedded into 670 vectors by basilica and then a logistic regression is fit to classify a hypothetical tweet. There are three ways to interact between python file and html file.  
* We use flask.request.values to access user entries through the html post method argument “name”. such as user1, user2, user3, user4, tweet_text, user_name
   * <form action="/compare" method="post">
   *  <select name="user1">
   * request.values['user1'],
   * <form action="/user" method="post">
   *         <input type="text" name="user_name" placeholder="Type a user">
   * request.values['user_name']
   * * in .py file we use arguments of render_template(), such as tweets, users, title, message to pass a value to jinja2 variables in html
   * {% for user in users %}
   *  <h1>{{ title }}</h1>
   * {% for tweet in tweets %}
   * return render_template('user.html', title=name, tweets=tweets, message=message)
   *   return render_template('base.html', title='Home', users=User.query.all())
   * * through jinja2 we add a variable to the route in GET method such as /user/{{ user.name }}. Then in .py we pass the variable to the function under the decorator.
   *  <a href="/user/{{ user.name }}">
   * @app.route('/user/<name>', methods=['GET'])
   *     def user(name=None, message=''):
### File Structure:
1. TwitOff                                #Project directory
* Pipfile
* Procfile
* .env
* twitoff                        # web app directory
   * __init__.py        # App point of entry, instantiate a flask app
   * app.py                # create app function, connect db, routings are here
   * models.py        # Data model for sqlalchemy db
   * twitter.py        # twitter api and basilica embedding
   * predict.py        # logistic regression model and predict function
   * templates        # sub directory containing the html templates
      * base.html        # Home page
      * user.html        # inherits from base and render the add user, or existing user page
      * prediction.html        # compare route 
____
Web Application Deployment-u3s3m4:
We are going to deploy the app on heroku. For that we need to use the postgreSQL instead of local sqlite db. follow these steps:
* on heroku platform create an app
* use heroku CLI to push your code to heroku
* on command prompt activate the virtual environment
* `heroku login` # heroku authorizations show if you are logged in heroku or not. 
* `pipenv install psycopg2-binary gunicorn`        #gunicorn is the production web server and runs the app instead of where we used flask running the app for development. gunicorn is faster and more scalable.
* use .env to set the ‘SQLALCHEMY_DATABASE_URI’ as it needs to switch to postgreSqL
* create a Procfile in project directory. This process file tell heroku how to run the app
* `heroku git:remote -a <heroku app name>`        # add heroku remote to git repository
* `git push heroku master`
* can see the log file by `heroku logs`
* .env is not pushed to heroku. we add twitter and basilica keys in settings>config Vars
* `heroku addons:create heroku-postgresql:hobby-dev`        #this on CLI will setup a postgres db for the app as an add-on in free tier and it calls is “DATABSE_URL”
* now on browser more>restart all dynos
* database is empty and wouldn’t run till we hit the /reset or /update route and create the database.
To avoid training the model everytime that we make a prediction we can serialize the model and save it as a file or string. dump(), load() are used to save it as a file and dumps, loads are used to dump and load it as a string.
* log_reg_string = pickle.dumps(log_reg)        # log_reg is the trained model
* log_reg_reloaded = pickle.loads(log_reg_string)
* log_reg_reloaded.predict()
* reg_file = open(‘logistic.model’, ‘wb’)
* pickle.dump(log_reg, reg_file)
* regfile = open(‘logistic.model’, ‘rb’)
* log_reg_load = pickle.load(regfile)
* log_reg 
