from subprocess import run
import glob
import json


files = glob.glob("./vid/*.webm")
video_list = "./video_metadata.json"


for f in files:
    print(f)
    results = run(
        [
            "ffprobe",
            "-loglevel",
            "0",
            "-print_format",
            "json",
            "-show_format",
            f,
        ],
        capture_output=True,
        text=True,
    )
    data = json.loads(results.stdout)
    tags = data["format"]["tags"]
    creation_date = tags.get("CREATION_DATE")
    location = tags.get("LOCATION")

    newObject = {
        "video": f,
        "creation_date": creation_date,
        "location": location
    }
    
    with open(video_list, "r") as file:
        video_list_data = json.load(file)
    video_list_data.append(newObject)
    with open(video_list, "w") as file:
        json.dump(video_list_data, file, indent=4)