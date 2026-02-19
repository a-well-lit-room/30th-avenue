import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(prog='30th-ave-filter', description='Filter through JSON data and create a filtered data set with only matching files.')

parser.add_argument('--input', '-i', type=str, required=True, help='Provide the path of a file or folder to analyze')
parser.add_argument('--output', '-o', type=str, required=True, help='Provide a location to save the output')

args = parser.parse_args()

input = Path(args.input)
output = args.output

with open(input, "r", encoding="utf-8") as f:
    items = json.load(f)  # expect a list of dicts

polygon_items = [item for item in items if item.get("inside_polygon") is True]

# write out or use
with open(output, "w", encoding="utf-8") as f:
    json.dump(polygon_items, f, indent=4)