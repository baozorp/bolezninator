FROM python:3.11

RUN apt-get update && apt-get install -y libgl1-mesa-glx

COPY requirements.txt .
RUN pip install -r requirements.txt


COPY . /ml_server
WORKDIR /ml_server

CMD ["python", "/ml_server/main.py"]
