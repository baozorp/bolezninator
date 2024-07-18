from uuid import uuid4
from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from helpers.image_helper import ImageHelper
from helpers.rpc_client import RPCClient
from models.response_models.upload_response_model import UploadResponseModel

router = APIRouter(prefix="/images")
rpcClient: RPCClient = RPCClient()

images_status: dict[str, int] = {}
images_count = 0
images_limit = 3


@router.post("/upload")
async def upload(file: UploadFile = File(...)) -> UploadResponseModel:
    global images_count, images_limit
    if images_count > images_limit:
        raise HTTPException(status_code=507, detail="Insufficient Storage")
    image_id = str(uuid4())
    image_path = ImageHelper.set_image_path(image_id=image_id)
    image_name = ImageHelper.get_image_name(image_path=image_path)
    img = await file.read()
    ImageHelper.save_image_in_bytes(image=img, image_path=image_path)
    rpcClient.send_image_name(image_name=image_name)
    images_status[image_name] = 1
    images_count += 1
    return UploadResponseModel(image_name=image_name)


@router.get("/download")
async def download_image(image_name: str, background_tasks: BackgroundTasks) -> FileResponse:
    image_path = ImageHelper.get_image_path(image_name="model"+image_name)
    if ImageHelper.is_image_exist(image_path=image_path):
        global images_count
        background_tasks.add_task(ImageHelper.remove_image, image_path)
        images_count -= 1
        return FileResponse(image_path, media_type='application/octet-stream', filename=image_name)
    elif image_name in images_status and images_status[image_name] != 3:
        raise HTTPException(status_code=425, detail="Too early")
    else:
        raise HTTPException(status_code=404, detail="File not found")


@router.post("/upload_from_ML")
async def upload_from_model(image_name: str, file=File(...)):
    image_path = ImageHelper.get_image_path(image_name="model"+image_name)
    content = await file.read()
    ImageHelper.save_image_in_bytes(image=content, image_path=image_path)
    images_status[image_name] = 3
    return


@router.get("/download_for_ML")
async def download_for_model(image_name: str, background_tasks: BackgroundTasks) -> FileResponse:
    image_path = ImageHelper.get_image_path(image_name=image_name)
    if ImageHelper.is_image_exist(image_path=image_path):
        background_tasks.add_task(ImageHelper.remove_image, image_path)
        images_status[image_name] = 2
        return FileResponse(image_path, media_type='application/octet-stream', filename=image_name)
    else:
        raise HTTPException(status_code=404, detail="File not found")
