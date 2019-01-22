import time, threading, pika
import settings

class RMQConnection(threading.Thread):
    def callback(self, ch, method, properties, body):
        # print(' [x] received %r' % (body,))
        self.queue.put(body)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue


    def run(self):
        self.URLparameters = pika.connection.URLParameters("amqp://sensors:sensors@{}:5672".format(settings.RABBITMQ))
        self.connection = pika.BlockingConnection(self.URLparameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="sensorData", durable=True, exclusive=False, auto_delete=False)
        self.channel.basic_consume(self.callback, queue='sensorData')
        print('start consuming')
        self.channel.start_consuming()