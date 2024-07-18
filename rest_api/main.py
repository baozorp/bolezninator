from fastapi import FastAPI
from routers.pictures_router import router as picture_router
import uvicorn


if __name__ == "__main__":
    app = FastAPI()
    app.include_router(picture_router)
    uvicorn.run(app, host="0.0.0.0", port=8080)
