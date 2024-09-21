from handlers.rpc_client import RPCClient
import os
from pathlib import Path
from ultralytics import YOLO
from dotenv import load_dotenv
import requests

if __name__ == "__main__":
    load_dotenv()
    _upload_dir: str = "uploads"
    os.makedirs(_upload_dir, exist_ok=True)
    weights_path = "helpers/weights/best.pt"
    inference_model = YOLO(weights_path)
    while True:
        try:
            print("start")
            RPCClient(inference_model).start_consuming()
        except Exception as e:
            print(e)
