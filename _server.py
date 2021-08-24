# from posixpath import basename
import uvicorn
from fastapi import FastAPI, Request, File, UploadFile
# from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from urllib.parse import urlparse
import urllib.request
from PIL import Image
import subprocess

app = FastAPI()

WORKING_DIRECTORY = os.getcwd()
TEMP_DIRECTORY = "temp"
PROCESSED_FOLDER = "./"
IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".bmp"]
STATIC_FILES_SERVER = "http://45.138.49.140:8000/data/" # 

########################
### ROUTES ###
########################

app.mount("/data", StaticFiles(directory=PROCESSED_FOLDER), name="data")

@app.get("/api")
async def extract_text(url: str = ""):
    if (url == ""):
        return {
            "success": False,
            "message": "Missing query parameter: url"
        }
    temp_file = download_file_to_disk(url)
    console_output = process_url(temp_file)
    if (console_output == ""):
        return {
            "success": False,
            "message": "Failed to process URL"
        }
    return build_response(temp_file, console_output)

########################
### HELPER FUNCTIONS ###
########################

def build_response(file, data):
    base_name = os.path.basename(file)
    extension = "." + base_name.split(".")[-1]
    output_file = ""
    if (extension in IMAGE_FORMATS):
        output_file = "predictions.jpg"
    else:
        output_file = "results.avi"

    return {
        "success": True,
        "path": STATIC_FILES_SERVER + output_file,
        "data": data
    }

def process_url(temp_file):
    base_name = os.path.basename(temp_file)
    extension = "." + base_name.split(".")[-1]
    output = ""
    try:
        if (extension in IMAGE_FORMATS):
            output = run_darknet_image(temp_file)
        else:
            output = run_darknet_video(temp_file)
    except Exception as e:
        print(e)
        output = ""
    return output


def run_darknet_image(file_name):
    base_name = os.path.basename(file_name)
    test = subprocess.Popen(["darknet",
                             "detector",
                             "test",
                             WORKING_DIRECTORY + "/cfg/coco.data",
                             WORKING_DIRECTORY + "/cfg/yolov4.cfg",
                             WORKING_DIRECTORY + "/yolov4.weights",
                             WORKING_DIRECTORY + "/" + TEMP_DIRECTORY + "/" + base_name,
                             "-dont_show",
                             "-ext_output"],
                            stdout=subprocess.PIPE)
    output = test.communicate()[0]
    return output

def run_darknet_video(file_name):
    base_name = os.path.basename(file_name)
    test = subprocess.Popen(["darknet",
                             "detector",
                             "demo",
                             WORKING_DIRECTORY + "/cfg/coco.data",
                             WORKING_DIRECTORY + "/cfg/yolov4.cfg",
                             WORKING_DIRECTORY + "/yolov4.weights",
                             WORKING_DIRECTORY + "/" + TEMP_DIRECTORY + "/" + base_name,
                             "-ext_output"],
                            stdout=subprocess.PIPE)
    output = test.communicate()[0]
    return output

def download_file_to_disk(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    parse_url = urlparse(url)
    base_name = os.path.basename(parse_url.path)
    temp_file = os.path.join(TEMP_DIRECTORY, base_name)
    try:
        req = urllib.request.Request(url, headers=headers)
        data = urllib.request.urlopen(req).read()
        with open(temp_file, 'wb') as f:
            f.write(data)
            f.close()
    except Exception as e:
            print(str(e))
    return temp_file

def get_data(temp_file):
    image = Image.open(temp_file)
    file_name = os.path.basename(temp_file)
    width, height = image.size
    return {
        "local_path": "/"+ TEMP_DIRECTORY +"/" + file_name,
        "remote_path": "/data/" + file_name,
        "width": width,
        "height": height
    }
########################
### START ###
########################

uvicorn.run(app, host="0.0.0.0", port=8000)