import sys # this allows me to access command line arguments
import argparse # this allows me to parse arguments
import os # this allows me to do stuff with searching directories
from os import listdir, makedirs
from os.path import isdir
from subprocess import run
import json

# create parser
parser = argparse.ArgumentParser(prog="resizevid", description="Compress a video using ffmpeg, and apply original creation time to new video.")

# add input and output arguments
parser.add_argument("-i", "--input", required=True, help="Input source file or directory.")
parser.add_argument("-o", "--output", required=True, help="Assign export directory.")

# add resizing factors
parser.add_argument("-s", "--scale", type=float, help="Resize the video based on a percentage of image size.")
parser.add_argument("-x", "--width", type=int, help="Resize a video based on a desired image width.")
parser.add_argument("-y", "--height", type=int, help="Resize a video based on a desired image height.")

# actually parse the input and create variables
args = parser.parse_args()
inputs= args.input
exports = args.output
scale = args.scale
width = args.width
height = args.height

# make sure that there is an input for some type of scaling
if (not scale) and (not width) and (not height):
    print("Please check your input. You must provide either a --scale argument or a dimensional argument like --width or --height.")
    sys.exit(1)

# add something that intelligently chooses a codec based on desired output container

# add filenames to videos list
if isdir(inputs) == True:
    videos = listdir(inputs)
    print("\ngathering source videos:")
    print(videos)
else:
    videos = [inputs]
    print("\ngathering source video:")
    print(videos)

# check if output directory already exists
if isdir(exports) != True:
    makedirs(exports)

# convert scale from percentage to a factor

if args.width and args.height:
    scaler = f"scale={width}:{height}"

if args.width and args.height != True:
    scaler = f"scale={width}:-1"

if args.height and args.width != True:
    scaler = f"scale=-1:{height}"

if args.scale:
    resize_factor = scale * 0.01
    scaler = f"scale=iw*{resize_factor}:ih*{resize_factor}"

for v in videos:
    # skip any hidden files like .ds_store
    if not v.startswith("."):
        # condition for working with a single file
        if v.startswith("/"):
            file_with_extension = os.path.split(v)[1]
            file_root = os.path.splitext(file_with_extension)[0]
            full_path_of_source_file = v
        # condition for working with a directory of files
        else:
            file_root = os.path.splitext(v)[0]
            full_path_of_source_file = f"{inputs}/{v}"
        new_name = f"{exports}/{file_root}.webm"
        print(f"v = {v}, file_root = {file_root}, full_path_of_source_file = {full_path_of_source_file}, new_name = {new_name}")

        # collect metadata for creation_time using ffprobe
        input_metadata = run(
            [
                "ffprobe",
                "-loglevel",
                "0",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                full_path_of_source_file,
            ],
            capture_output=True,
            text=True
        )

        # i'm calling it creation_date since ffmpeg won't let me add a custom metadata field called creation_time
        data = json.loads(input_metadata.stdout)
        tags = data["format"]["tags"]
        creation_date = tags.get("creation_time")
        print(creation_date)

        # add extracted metadata to output
        print("now transcoding your files...")
        run(
            [
                "ffmpeg",
                "-i",
                full_path_of_source_file,
                "-movflags",
                "use_metadata_tags",
                "-metadata",
                f"creation_date={creation_date}",
                "-c:v",
                "libvpx",
                "-b:v",
                "200K",
                "-vf",
                scaler,
                "-c:a",
                "libvorbis",
                "-y",
                new_name
            ]
        )
        print(f"{new_name} has been created!")


# how to add an argument to customize the renaming convention?