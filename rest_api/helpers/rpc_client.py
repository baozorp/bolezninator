import pika
import time


class RPCClient:
    def __init__(self):
        self.queue_name = "apis_sended_ids"
        self.connect()

    def connect(self):
        while True:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='rabbitmq', port=5672, heartbeat=30, blocked_connection_timeout=300))
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name)
                break
            except Exception as e:
                print(f"Failed to connect to RabbitMQ: {e}")
                time.sleep(3)

    def send_image_name(self, image_name: str):
        for _ in range(0, 10):
            try:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.queue_name,
                    body=image_name
                )
                print(f"Sent image with id {image_name} to model")
                break
            except Exception as e:
                self.connect()
                print(f"Failed to send image ID: {e}")
