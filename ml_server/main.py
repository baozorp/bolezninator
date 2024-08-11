from handlers.rpc_client import RPCClient
import os
from pathlib import Path
from ultralytics import YOLO

if __name__ == "__main__":
    _upload_dir: str = "uploads"
    os.makedirs(_upload_dir, exist_ok=True)
    path = Path(r'/ml_server/helpers/weights/best.pt')
    inference_model = YOLO(path)
    while True:
        try:
            print("start")
            RPCClient(inference_model).start_consuming()
        except Exception as e:
            print(e)
