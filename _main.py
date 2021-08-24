import uvicorn
# import subprocess
import os
import urllib.request
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
from fastapi.staticfiles import StaticFiles
import shutil

source="predictions.jpg"
destination="static"

app = FastAPI()

class Item(BaseModel):
    url: str

app.mount("/static", StaticFiles(directory="static"), name="static")


def download_image(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    try:
        req = urllib.request.Request(url, headers=headers)
        data = urllib.request.urlopen(req).read()
        with open("file.jpg", 'wb') as f:
            f.write(data)
            f.close()
    except Exception as e:
        print(str(e))


def run_darknet():
    test = subprocess.Popen(["darknet",
                             "detector",
                             "test",
                             "C:\\Users\\sesha\\Untitled Folder\\darknet_alexeyAB\\build\\darknet\\x64\\cfg\\coco.data",
                             "C:\\Users\\sesha\\Untitled Folder\\darknet_alexeyAB\\build\\darknet\\x64\\cfg\\yolov4.cfg",
                             "C:\\Users\\sesha\\Untitled Folder\\darknet_alexeyAB\\build\\darknet\\x64\\yolov4.weights",
                             "file.jpg",
                             "-dont_show",
                             "-ext_output"],
                            stdout=subprocess.PIPE)
    output = test.communicate()[0]
    return output


def serve_image():
    os.remove("static/predictions.jpg")
    return shutil.move(source,destination)


@app.get('/api') #decorator
def index(url: str = ""):
    print("Attempting to download image from URL: " + url)

    # Download video from URL
    download_image(url)

    # Send downloaded video to darknet
    output = run_darknet()

    # Move predictions to static folder
    new_path=serve_image()

    # return to API
    return {"message": "success", "image": "http://45.138.49.140:8000/" + new_path.replace("\\","/"), "data": output}


@app.post("/api/")
async def upload_video(item: Item):
    # Capture video url
    url = item.url
    print("Attempting to download image from URL: " + url)

    # Download video from URL
    download_image(url)

    # Send downloaded video to darknet
    output = run_darknet()

    # Move predictions to static folder
    new_path=serve_image()

    # return to API
    return {"message": "success", "image": "http://45.138.49.140:8000/" + new_path.replace("\\","/"), "data": output}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
