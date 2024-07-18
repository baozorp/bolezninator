import pika
import time
import requests
from helpers.image_helper import ImageHelper
from PIL import Image


class RPCClient:
    def __init__(self):
        self.queue_name = "apis_sended_ids"
        self.exchange = "api_exchange"
        self.connect()

    def connect(self):
        while True:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='rabbitmq', port="5672"))

                self.channel = self.connection.channel()
                self.channel.basic_consume(queue=self.queue_name,
                                           on_message_callback=self._on_message)
                break
            except Exception as e:
                print(f"Failed to connect to RabbitMQ: {e}")
                time.sleep(3)

    def _on_message(self, ch, method, props, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        image_name = str(body)[2:-1]
        url = f"http://rest_api:8080/images/download_for_ML?image_name={
            image_name}"
        response = requests.get(url)
        time.sleep(1)
        if response.status_code == 200:
            print(image_name)
            image_jpeg: Image.Image = ImageHelper.convert_image(
                response.content)
            image_jpeg = ImageHelper.add_watermark(image_jpeg)
            image_jpeg_to_responce = ImageHelper.image_to_bytes(image_jpeg)
        url = f"http://rest_api:8080/images/upload_from_ML?image_name={
            image_name}"
        print(requests.post(url, files={
              "file": image_jpeg_to_responce}).status_code)

    def start_consuming(self):
        print(" [x] Awaiting RPC requests")
        self.channel.start_consuming()


RPCClient().start_consuming()
