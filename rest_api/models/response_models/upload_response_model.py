from pydantic import BaseModel


class UploadResponseModel(BaseModel):
    image_name: str

