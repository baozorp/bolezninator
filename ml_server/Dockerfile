FROM python:3.11

WORKDIR /ml_server
RUN apt-get update && apt-get install -y libgl1-mesa-glx
ADD https://github.com/Sunests/x-ray-best-model/raw/refs/heads/main/best.pt?download= ./helpers/weights/best.pt

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "/ml_server/main.py"]
