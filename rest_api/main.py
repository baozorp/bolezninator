from fastapi import FastAPI, WebSocket
from routers.pictures_router import router as picture_router
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8080,
        ssl_keyfile="/app/certificate.key",  # путь к вашему файлу ключа
        ssl_certfile="/app/certificate.crt"  # путь к вашему файлу сертификата
    )
