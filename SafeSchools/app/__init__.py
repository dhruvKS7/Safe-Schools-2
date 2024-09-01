import os
import sqlalchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from yaml import load, Loader

def init():
    if os.environ.get('GAE_ENV') != 'standard':
        try:
            variables = load(open("app.yaml"), Loader=Loader)
        except OSError as e:
            print("Make sure you have the app.yaml file setup")
            os.exit()
        env_variables = variables['env_variables']
        for var in env_variables:
            os.environ[var] = env_variables[var]
    pool = sqlalchemy.create_engine (
        url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
            os.environ.get('MYSQL_USER'), os.environ.get('MYSQL_PASSWORD'), os.environ.get('MYSQL_HOST'), 3306, os.environ.get('MYSQL_DB')
        )
    )

    return pool

app = Flask(__name__)

db = init()

from app import routes