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
        # width, height = image.size
        # draw = ImageDraw.Draw(image)
        # font_size = int(height / 20)
        # font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        # text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        # text_width = text_bbox[2] - text_bbox[0]
        # text_height = text_bbox[3] - text_bbox[1]
        # x, y = width - text_width - 100, height - text_height - 100
        # draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
        return image

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
