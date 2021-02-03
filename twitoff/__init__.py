"""
Entry point for twitoff
TO launch a local server, run this from the base directory:
FLASK_APP=twitoff flask run
"""
from .app import create_app

APP = create_app()
