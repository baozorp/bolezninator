import pika
import time
import requests
from helpers.image_helper import ImageHelper
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
import logging
import certifi

class RPCClient:
    
    _inference_model: YOLO

    def __init__(self, inference_model: YOLO):
        self.queue_name = "apis_sended_ids"
        self.exchange = "api_exchange"
        self._inference_model = inference_model
        self.connect()

    def connect(self):
        while True:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='rabbitmq', port="5672"))

                self.channel = self.connection.channel()
                self.channel.basic_consume(queue=self.queue_name,
                                           on_message_callback=self._on_message)
                print("CONNECTED==================================================")
                break
            except Exception as e:
                print(f"Failed to connect to RabbitMQ: {e}")
                time.sleep(3)

    def _on_message(self, ch, method, props, body):
        logging.info("NEW MESSAGE ==================================================")
        try:
            print("TRY========================================================================", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            image_name = str(body)[2:-1]
            url = f"https://api:8080/images/download_for_ML?image_name={image_name}"
            response = requests.get(url, verify=False)
            response.raise_for_status()
            image_bytes = response.content

            image_jpeg: Image.Image = ImageHelper.convert_image(image_bytes)
            inference_result = self._inference_model.predict(image_jpeg, conf=0.01, save=False, imgsz=1024) # type: ignore
            image_in_memory = BytesIO()
            for result in inference_result:
                # boxes = result.boxes
                # masks = result.masks
                # probs = result.probs
                result.save(f"./uploads/{image_name}")
                break
            image_jpeg = Image.open(f"./uploads/{image_name}")
            image_jpeg = ImageHelper.add_watermark(image_jpeg)
            image_jpeg_to_responce = ImageHelper.image_to_bytes(image_jpeg)
            url = f"https://api:8080/images/upload_from_ML?image_name={image_name}"
            requests.post(url, verify=False, files={
                "file": image_jpeg_to_responce}).status_code
        except Exception as e:
            print(e)

    def start_consuming(self):
        print(" [x] Awaiting RPC requests")
        self.channel.start_consuming()
