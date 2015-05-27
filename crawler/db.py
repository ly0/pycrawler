import motor
from .default_settings import *

mongo_connection = motor.MotorClient('localhost', 27017)
mongo_database = 'pycrawler'
mongo_client = mongo_connection[mongo_database]