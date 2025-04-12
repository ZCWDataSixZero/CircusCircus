"""
Flask configuration variables.
"""
from os import environ, path
import os


basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '.env'))

class Config:
    """Set Flask configuration from .env file."""
    # General Config
    SECRET_KEY = 'kristofer'
    FLASK_APP = 'forum.app'

    # Database
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///circuscircus.db'
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flaskuser:flaskpass@mysql-db:3306/flaskdb'
# Configure MySQL connection
    mysql_host = os.environ.get('MYSQL_HOST', 'mysql-db')
    mysql_user = os.environ.get('MYSQL_USER', 'flaskuser')
    mysql_password = os.environ.get('MYSQL_PASSWORD', 'flaskpass')
    mysql_db = os.environ.get('MYSQL_DB', 'flaskdb')
    mysql_port = os.environ.get('MYSQL_PORT', '3307')

    # Configure SQLAlchemy
    #app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@mysql-db/{mysql_db}'
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{mysql_user}:{mysql_password}@mysql-db/{mysql_db}'

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
