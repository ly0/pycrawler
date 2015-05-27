from .consumer import Consumer
from .publisher import Publisher
from .default_settings import *

def consumer_message_handler(basic_deliver, properties, body):
    pass
consumer = Consumer(RABBITMQ_URI, queue=TASK_QUEUE, routing_key=TASK_QUEUE_ROUTING_KEY, on_message_callback=consumer_message_handler)
publisher = Publisher(RABBITMQ_URI, queue=TASK_QUEUE, routing_key=TASK_QUEUE_ROUTING_KEY)

