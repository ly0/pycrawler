import os

_work_path = os.getcwd()


MONGO_USERNAME = 'test'
MONGO_PASSWORD = 'test'


RABBITMQ_URI = 'amqp://guest:guest@localhost:5672/%2F'
TASK_QUEUE = 'pycrawler_tasks'
TASK_QUEUE_ROUTING_KEY = 'pycrawler_tasks'

from settings import *