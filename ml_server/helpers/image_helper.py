import os
import io
from PIL import Image, ImageDraw, ImageFont


class ImageHelper:

    _upload_dir: str = "uploads"
    _image_format: str = ".jpg"
    os.makedirs(_upload_dir, exist_ok=True)

    @staticmethod
    def save_image(image: Image.Image, image_path: str):
        image.save(image_path, "JPEG")

    @staticmethod
    def get_image_path(image_name: str):
        return os.path.join(ImageHelper._upload_dir, image_name)

    @staticmethod
    def is_image_exist(image_path: str):
        return os.path.exists(image_path)

    @staticmethod
    def convert_image(content: bytes) -> Image.Image:
        with Image.open(io.BytesIO(content)) as img:
            img = img.convert("RGB")
            return img

    @staticmethod
    def add_watermark(image: Image.Image, watermark_text: str = "ВСЕГЕИ") -> Image.Image:
        watermark = Image.open("/ml_server/helpers/images/watermark.png").convert("RGBA")
        watermark = watermark.resize(image.size, resample=Image.Resampling.LANCZOS)

        watermark = watermark.convert("RGBA")
        alpha = watermark.split()[3]
        alpha = alpha.point(lambda p: p * 100 / 100)
        watermark.putalpha(alpha)
        combined = Image.new('RGBA', image.size)
        combined.paste(image.convert("RGBA"), (0, 0))
        combined.paste(watermark, (0, 0), mask=watermark)

        return combined.convert("RGB")

    @staticmethod
    def image_to_bytes(image: Image.Image) -> bytes:
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format='JPEG')
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    @staticmethod
    def remove_image(image_path: str) -> None:
        try:
            os.remove(image_path)
        except Exception as e:
            print(f"Can't remove image for reasons: {e}")
