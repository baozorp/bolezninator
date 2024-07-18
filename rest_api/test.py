import requests

url = "https://193.232.208.28:9500/pictures/upload"
file_path = "1.jpg"
with open(file_path, "rb") as file:
    response = requests.post(url, files={"file": file})

if response.status_code == 200:
    picture_id = response.json()["picture_id"]
    url = f"https://193.232.208.28:9500/pictures/download?picture_id={
        picture_id}"
    response = requests.get(url)

    if response.status_code == 200:
        with open(f"{picture_id}.jpg", "wb") as file:
            file.write(response.content)
        print("File downloaded successfully.")
    else:
        print("Error:", response.json())
