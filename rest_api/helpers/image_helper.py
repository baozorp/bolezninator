import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

class ImageHelper:

    _upload_dir: str = "uploads"
    _image_format: str = ".jpg"
    os.makedirs(_upload_dir, exist_ok=True)

    @staticmethod
    def save_image_in_bytes(image: bytes, image_path: str):
        with open(image_path, "wb") as image_file:
            image_file.write(image)

    @staticmethod
    def get_image_name(image_path: str):
        return os.path.basename(image_path)

    @staticmethod
    def get_image_path(image_name: str):
        return os.path.join(ImageHelper._upload_dir, image_name)

    @staticmethod
    def set_image_path(image_id: str):
        return os.path.join(ImageHelper._upload_dir, f"{image_id}{ImageHelper._image_format}")

    @staticmethod
    def is_image_exist(image_path: str):
        return os.path.exists(image_path)

    @staticmethod
    def add_watermark(image: Image.Image, watermark_text: str = "Нейроскан") -> Image.Image:
        width, height = image.size
        draw = ImageDraw.Draw(image)
        font_size = int(height / 20)
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x, y = width - text_width - 100, height - text_height - 100
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
        return image

    @staticmethod
    def remove_image(
            image_path: str,
            image_name: str,
            images_status: dict[str, int],
            images_dates: dict[datetime, str],
            images_count: dict[str, int]
            ) -> None:
        try:
            os.remove(image_path)
            del images_status[image_name]
            print("deleted status")
            key_to_remove = None
            for key, value in images_dates.items():
                if value == image_name:
                    key_to_remove = key
                    break
            print("deleted date")
            if key_to_remove:
                del images_dates[key_to_remove]
                print("finded date")
            else:
                raise Exception("Cant find date")
            images_count["count"] -= 1
        except Exception as e:
            print(f"Can't remove image for reasons: {e}")

    @staticmethod
    def remove_image_for_ml(image_path: str) -> None:
        try:
            os.remove(image_path)
        except Exception as e:
            print(f"Can't remove image for reasons: {e}")