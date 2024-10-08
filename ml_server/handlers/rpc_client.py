import pika
import time
import requests
from helpers.image_helper import ImageHelper
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
import os



class RPCClient:
    
    _inference_model: YOLO

    def __init__(self, inference_model: YOLO):
        self.queue_name = "apis_sended_ids"
        self.exchange = "api_exchange"
        self._inference_model = inference_model
        self.names_dict = [
            ('heart', 'сердце'),
            ('lungs', 'легкие'),
            ('trachea', 'трахея'),
            ('bronchitis', 'бронхит'),
            ('pneumonia/bronchopneumonia', 'пневмония/бронхопневмония'),
            ('pulmonary edema', 'отек легких'),
            ('hydrothorax', 'гидроторакс'),
            ('pneumothorax', 'пневмоторакс'),
            ('tracheal collapse', 'коллапс трахеи'),
            ('neoplasm', 'новобразования'),
            ('atelectasis', 'ателектаз')
        ]
        self.connect()

    def connect(self):
        while True:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='rabbitmq', port="5672"))

                self.channel = self.connection.channel()
                self.channel.basic_consume(queue=self.queue_name,
                                           on_message_callback=self._on_message)
                print("====================CONNECTED==============================")
                break
            except Exception as e:
                print(f"Failed to connect to RabbitMQ: {e}")
                time.sleep(3)

    def _on_message(self, ch, method, props, body):
        print("======================NEW MESSAGE =========================")
        try:
            print("============================TRY======================")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            image_name = str(body)[2:-1]
            download_url = ""
            upload_url = ""
            is_test = os.getenv("IS_TEST")
            download_url = f"http{'s' if not is_test else ''}://api:8080/images/download_for_ML?image_name={image_name}"
            upload_url = f"http{'s' if not is_test else ''}://api:8080/images/upload_from_ML?image_name={image_name}"
            upload_description_url = f"http{'s' if not is_test else ''}://api:8080/images/upload_description_ML"
            response = requests.get(download_url, verify=False)
            response.raise_for_status()
            image_bytes = response.content
            image_jpeg: Image.Image = ImageHelper.convert_image(image_bytes)
            inference_result = self._inference_model.predict(image_jpeg, conf=0.01, save=False, imgsz=1024)
            max_score_boxes: dict[str, float] = {}
            max_score_boxes_final: dict[str, float]= {}
            if not inference_result[0] or not inference_result[0].boxes:
                data = {"image_name": image_name, "description": {"Найдено болезней": 0}}
                description_response = requests.post(upload_description_url, verify=False, json=data)
                requests.post(upload_url, verify=False, files={
                    "file": image_bytes})
                print("Говно")
                return
            classes = inference_result[0].boxes.cls
            desired_classes = [3, 4, 5, 6, 7, 8, 9, 10]
            filtered_results = inference_result[0][[i for i, cls in enumerate(classes) if cls in desired_classes]]
            
            if not filtered_results.boxes:
                raise ValueError
            for cls, score in zip(filtered_results.boxes.cls, filtered_results.boxes.conf):
                cls_name = self.names_dict[int(cls)][1]
                if cls_name not in max_score_boxes:
                    max_score_boxes[cls_name] = float(score)
                else:
                    if max_score_boxes[cls_name] < float(score):
                        max_score_boxes[cls_name] = float(score)
            
            for key, value in max_score_boxes.items():
                max_score_boxes_final[key] = value
            classes = filtered_results.boxes.cls
            scores = filtered_results.boxes.conf
            filtered_results = filtered_results[[i for i, score in enumerate(scores) if score in max_score_boxes.values()]]
            inference_result[0] = filtered_results
            result_image = inference_result[0].plot(boxes=True)
            result_image = Image.fromarray(result_image)
            image_jpeg = ImageHelper.add_watermark(result_image)
            image_jpeg_to_responce = ImageHelper.image_to_bytes(image_jpeg)
            data = {"image_name": image_name, "description": max_score_boxes_final}
            description_response = requests.post(upload_description_url, verify=False, json=data)
            description_response.raise_for_status()
            requests.post(upload_url, verify=False, files={
                "file": image_jpeg_to_responce})
        except Exception as e:
            print(e)

    def start_consuming(self):
        print(" [x] Awaiting RPC requests")
        self.channel.start_consuming()