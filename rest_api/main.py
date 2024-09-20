from fastapi import FastAPI
from routers.pictures_router import router as picture_router
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

app = FastAPI()
app.include_router(picture_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

if __name__ == "__main__":
    load_dotenv()
    is_test = os.getenv("IS_TEST")
    uvicorn_config = uvicorn.Config(app=app, host="0.0.0.0", port=8080)
    if not is_test:
        uvicorn_config.ssl_keyfile = "/app/certificate.key"
        uvicorn_config.ssl_certfile = "/app/certificate.crt"
    uvicorn.Server(uvicorn_config).run()
