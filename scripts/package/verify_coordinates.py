import json
from typing import Iterable, List, Tuple, Union
from shapely.geometry import Point, Polygon

Coord = Tuple[float, float] # (longitude, latitude)

def load_polygon_from_json(path: str, lat: str = 'lat', lon: str = 'lon') -> Polygon:
    # loads a json file with coordinates and returns a shapely Polygon
    with open(path, 'r') as f:
        data = json.load(f)
    coords: List[Coord] = [(item[lon], item[lat]) for item in data]
    return Polygon(coords)

def load_points_from_json(path: str, lat: str = 'latitude', lon: str = 'longitude') -> List[Coord]:
    # loads a json file with points and returns a list of (lon, lat) tuples
    with open(path, 'r') as f:
        data = json.load(f)
    return [(item[lon], item[lat]) for item in data]

def check_points_in_polygon(
    polygon: Polygon,
    points: Iterable[Coord],
    inclusive: bool = True
    ) -> List[bool]:
    if inclusive:
        return [polygon.covers(Point(lon, lat)) for lon, lat in points] # includes boundary
    else:
        return [polygon.contains(Point(lon, lat)) for lon, lat in points] # excludes boundary
    
def verify_coordinates(
    polygon_path: str,
    points_path: str,
    lat_poly: str = 'lat',
    lon_poly: str = 'lng',
    lat_points: str = 'latitude',
    lon_points: str = 'longitude',
    inclusive: bool = True
    ) -> List[bool]:
    polygon = load_polygon_from_json(polygon_path, lat=lat_poly, lon=lon_poly)
    points = load_points_from_json(points_path, lat=lat_points, lon=lon_points)
    return check_points_in_polygon(polygon, points, inclusive=inclusive)

# make a json file that copies the points json file but adds a "inside_polygon" key
def make_verified_json(
    polygon_path: str,
    points_path: str,
    output_path: str,
    lat_poly: str = 'lat',
    lon_poly: str = 'lng',
    lat_points: str = 'latitude',
    lon_points: str = 'longitude',
    inclusive: bool = True
    ) -> None:
    polygon = load_polygon_from_json(polygon_path, lat=lat_poly, lon=lon_poly)
    with open(points_path, 'r') as f:
        data = json.load(f)
    results = check_points_in_polygon(
        polygon,
        [(item[lon_points], item[lat_points]) for item in data],
        inclusive=inclusive
    )
    for item, inside in zip(data, results):
        item['inside_polygon'] = inside
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)