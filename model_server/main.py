from rpc_client import RPCClient
import os

if __name__ == "__main__":
    _upload_dir: str = "uploads"
    os.makedirs(_upload_dir, exist_ok=True)
    while True:
        try:
            RPCClient().start_consuming()
        except Exception as e:
            print(e)
