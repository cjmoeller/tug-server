import pika
import struct
# Create a global channel variable to hold our channel object in
channel = None

# Step #2
def on_connected(connection):
    """Called when we are fully connected to RabbitMQ"""
    # Open a channel
    connection.channel(on_channel_open)

# Step #3
def on_channel_open(new_channel):
    """Called when our channel has opened"""
    global channel
    channel = new_channel
    channel.queue_declare(queue="sensorData", durable=True, exclusive=False, auto_delete=True, callback=on_queue_declared)

# Step #4
def on_queue_declared(frame):
    """Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
    channel.basic_consume(handle_delivery, queue='sensorData')

# Step #5
def handle_delivery(channel, method, header, body):
    """Called when we receive a message from RabbitMQ"""
    measurement_type = body[0]
    time = struct.unpack('>q',body[1:9])

    v1 = struct.unpack('>f', body[9:13])
    v2 = struct.unpack('>f', body[13:17])
    v3 = struct.unpack('>f', body[17:21])

    print("TYPE: " + str(measurement_type) + " | " + str(time) + " Measurement(" + str(v1) + " | " + str(v2) + " | " + str(v3) + ")")

# Step #1: Connect to RabbitMQ using the default parameters
parameters = pika.connection.URLParameters("amqp://sensors:sensors@iuppiter.fritz.box:5672")
connection = pika.SelectConnection(parameters, on_connected)

try:
    # Loop so we can communicate with RabbitMQ
    connection.ioloop.start()
except KeyboardInterrupt:
    # Gracefully close the connection
    connection.close()
    # Loop until we're fully closed, will stop on its own
    connection.ioloop.start()