# Standard library
import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date, time, datetime
from pathlib import Path
import tempfile
from typing import Optional

# Third-party
from pymediainfo import MediaInfo
from package.verify_coordinates import verify_coordinates, make_verified_json

@dataclass
class File:
    filename: str
    checksum: str
    # latitude: float
    # longitude: float
    # altitude: float
    creation_date: Optional[date]
    creation_time: Optional[time]
    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]
    inside_polygon: Optional[bool] = None

def get_creation_data():
    # build a parser for the user to interact with
    parser = argparse.ArgumentParser(description='Get GPS coordinates and creation time of a file or a folder of files')
    parser.add_argument('--input', '-i', type=str, required=True, help='Provide the path of a file or folder to analyze')
    parser.add_argument('--output', '-o', type=str, help='Provide a location to save the output')
    
    args = parser.parse_args()
    
    input=Path(args.input)
    output=args.output

    # function to get sha256 checksum of a file
    def sha256(path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            # Read and update hash string value in blocks of 8K
            for byte_block in iter(lambda: f.read(8192), b""):
                h.update(byte_block)
        return h.hexdigest()

    # gets coordinates from .mov files
    def get_coordinates(track):

        # TODO: change key to a list to make it happy with metadata for other file formats
        #   check compliance of the below keys
        # for key in ('comapplequicktimelocationiso6709', 'location', 'gps_location', 'GPSLatitude', 'GPSLongitude', 'locationeng'):
        key = 'comapplequicktimelocationiso6709'
        val = getattr(track, key, None) if hasattr(track, key) else None

        # pulls the full ISO string and break it up the coordinates into each axis
        if isinstance(val, str):
            # ISO6709 example: "+51.5074+000.1278/"
            import re
            m = re.match(r'([+-]\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)/?', val)
            if m:
                lat = float(m.group(1))
                lon = float(m.group(2))
                alt = float(m.group(3))
                return lat, lon, alt
            else:
                print("    no coordinates")
                return None, None, None
        else:
            print("    no coordinates")
            return None, None, None

    # gets the timestamp of when the media was created
    def get_creation_time(track):

        # TODO: change key to a list to make it happy with metadata for other file formats
        #   check compliance of the below keys
        # for key in ("tagged_date", "encoded_date", "creation_time", "comapplequicktimecreationdate", "file_created_date", "file_last_modification_date"):
        #     print(key, getattr(track, key, None) if hasattr(track, key) else None)
        key = "comapplequicktimecreationdate"
        val = getattr(track, key, None) if hasattr(track, key) else None

        # gets the full string as formatted for iPhones and interprets the date and time
        if isinstance(val, str):
            # Example: "2023-10-01T12:34:56+00:00"
            if re.match(r'.*[+-]\d{4}$', val):
                # the metadata is showing up without the colon for the time zone difference
                    # (e.g. '-0400' instead of '-04:00')
                val = val[:-2] + ':' + val[-2:]    # -> '2024-06-09T12:25:04-04:00'
            dt = datetime.fromisoformat(val)
            return dt.date(), dt.time()
        else:
            print("    no creation time")
            return None, None
        
    # analyze a file
    def analyze_media(file) -> File:
        # get checksum of file
        checksum = sha256(file)

        # get the media info
        media_info = MediaInfo.parse(file)

        for track in media_info.tracks:
            if track.track_type == 'General':
                # print(track.to_data().keys())   # raw keys
                lat, lon, alt = get_coordinates(track)
                creation_date, creation_time = get_creation_time(track)
                # return lat, lon, alt, creation_date, creation_time
                # print(Path(file).name, checksum, lat, lon, alt, creation_date, creation_time)

                if lat and lon:
                    # check if lat and lon are within polygon
                    poly = 'polygon_coordinates.json'
                    formatted_data = json.dumps([{
                        'latitude': lat,
                        'longitude': lon
                    }])

                    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
                        tf.write(formatted_data)        # formatted_data is JSON string
                        points_path = tf.name
                    results = verify_coordinates(poly, points_path)
                    print(results)
                else:
                    results = []

                return File(
                    filename=str(Path(file).resolve()),
                    checksum=checksum,
                    latitude=lat,
                    longitude=lon,
                    altitude=alt,
                    creation_date=creation_date,
                    creation_time=creation_time,
                    inside_polygon=results[0] if results else None
                )
            
    # make a csv file
    def make_csv(data, output):
        header = ['Filename', 'Checksum', 'Latitude', 'Longitude', 'Altitude', 'Creation Date', 'Creation Time']
        path = Path(output)
        with path.open('w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for file in data:
                writer.writerow([
                    file.filename,
                    file.checksum,
                    file.latitude,
                    file.longitude,
                    file.altitude,
                    file.creation_date,
                    file.creation_time,
                    file.inside_polygon
                ])
    
    # make a json file
    def make_json(data, output):
        path = Path(output)
        serialized_data = []
        for file in data:
            serialized_data.append({
                'filename': file.filename,
                'checksum': file.checksum,
                'latitude': file.latitude,
                'longitude': file.longitude,
                'altitude': file.altitude,
                'creation_date': file.creation_date.isoformat() if file.creation_date else None,
                'creation_time': file.creation_time.isoformat() if file.creation_time else None,
                'inside_polygon': file.inside_polygon
            })
        with path.open('w', encoding='utf-8') as f:
            json.dump(serialized_data, f, indent=4)

    # check if input is a file or a folder
    if input.is_file():
        f = analyze_media(input)
        data = [f]
    elif input.is_dir():
        
        # makes a container for the File objects of each media file
        data = []

        for file in input.iterdir():
            if file.is_file():
                # skip non-media files
                # if not file.suffix.lower() in ('.mov', '.mp4', '.avi', '.mkv', '.jpg', '.jpeg', '.png', '.heic', '.tiff'):
                #     continue

                # needs the comma for single-element tuples
                if not file.suffix.lower() in ('.mov',):
                    continue
                print('Analyzing:', file.name)
                f = analyze_media(file)
                data.append(f)
    else:
        print('Input path is not valid.')
        exit()

    # TODO: check if output path is valid
    if not output:
        # print to terminal in json format
        serialized_data = []
        for file in data:
            serialized_data.append({
                'filename': file.filename,
                'checksum': file.checksum,
                'latitude': file.latitude,
                'longitude': file.longitude,
                'altitude': file.altitude,
                'creation_date': file.creation_date.isoformat() if file.creation_date else None,
                'creation_time': file.creation_time.isoformat() if file.creation_time else None,
                'inside_polygon': file.inside_polygon
            })
        print(json.dumps(serialized_data, indent=4))
    elif output.lower().endswith('.csv'):
        make_csv(data, output)
    elif output.lower().endswith('.json') or output.lower().endswith('.txt'):
        make_json(data, output)
    else:
        print('Output is not destined for a valid format.')

# on script run 
if __name__ == '__main__':
    get_creation_data()