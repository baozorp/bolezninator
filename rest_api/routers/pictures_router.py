from uuid import uuid4
from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from helpers.image_helper import ImageHelper
from helpers.rpc_client import RPCClient
from models.response_models.upload_response_model import UploadResponseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/images")
rpcClient: RPCClient = RPCClient()

images_status: dict[str, int] = {}
images_dates: dict[datetime, str] = {}
images_count: dict[str, int] = {"count": 0}
images_limit = 150


@router.post("/upload")
async def upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> UploadResponseModel:
    global images_count, images_limit, images_dates
    if images_count["count"] > images_limit:
        min_date = min(images_dates.keys())
        if min_date:
            current_time = datetime.now() - timedelta(minutes=1)
            five_minutes_ago = current_time
            if min_date > five_minutes_ago:
                raise HTTPException(status_code=507, detail="Insufficient Storage")
            else:
                earliest_image_name = images_dates[min_date]
                image_path = ImageHelper.get_image_path(image_name=earliest_image_name)
                image_path_of_model_images = ImageHelper.get_image_path(image_name="model"+earliest_image_name)
                if ImageHelper.is_image_exist(image_path=image_path):
                    ImageHelper.remove_image(image_path, earliest_image_name, images_status, images_dates, images_count)
                    print("deleted last image")
                elif ImageHelper.is_image_exist(image_path=image_path_of_model_images):
                    ImageHelper.remove_image(image_path_of_model_images, earliest_image_name, images_status, images_dates, images_count)
                    print("deleted last image")
                else:
                    print("Image not exist")
    image_id = str(uuid4())
    image_path = ImageHelper.set_image_path(image_id=image_id)
    image_name = ImageHelper.get_image_name(image_path=image_path)
    img = await file.read()
    ImageHelper.save_image_in_bytes(image=img, image_path=image_path)
    rpcClient.send_image_name(image_name=image_name)
    images_status[image_name] = 1
    images_count["count"] += 1
    images_dates[datetime.now()] = image_name
    return UploadResponseModel(image_name=image_name)


@router.get("/download")
async def download_image(image_name: str, background_tasks: BackgroundTasks) -> FileResponse:
    image_path = ImageHelper.get_image_path(image_name="model"+image_name)
    if ImageHelper.is_image_exist(image_path=image_path):
        global images_count, images_status, images_dates
        background_tasks.add_task(ImageHelper.remove_image, *[image_path, image_name, images_status, images_dates, images_count])
        return FileResponse(image_path, media_type='application/octet-stream', filename=image_name)
    elif image_name in images_status and images_status[image_name] != 3:
        raise HTTPException(status_code=425, detail="Too early")
    else:
        raise HTTPException(status_code=404, detail="File not found")


@router.post("/upload_from_ML")
async def upload_from_model(image_name: str, file=File(...)):
    global images_status
    image_path = ImageHelper.get_image_path(image_name="model"+image_name)
    content = await file.read()
    ImageHelper.save_image_in_bytes(image=content, image_path=image_path)
    images_status[image_name] = 3
    return


@router.get("/download_for_ML")
async def download_for_model(image_name: str, background_tasks: BackgroundTasks) -> FileResponse:
    global images_status
    image_path = ImageHelper.get_image_path(image_name=image_name)
    if ImageHelper.is_image_exist(image_path=image_path):
        background_tasks.add_task(ImageHelper.remove_image_for_ml, image_path)
        images_status[image_name] = 2
        return FileResponse(image_path, media_type='application/octet-stream', filename=image_name)
    else:
        raise HTTPException(status_code=404, detail="File not found")
