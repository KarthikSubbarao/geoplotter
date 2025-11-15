# geoplotter
Geo Coord Visualizer of Locations and Polygons Boundaries that interacts with Valkey.

It uses both standard GEO commands and the new Valkey Geofence module commands for advanced spatial operations.

## Features

### Standard GEO Commands
- Add location markers and save to Valkey using GEOADD
- Draw polygons and search for locations within boundaries using GEOSEARCH
- Load and visualize existing geo data from Valkey

### Geofence Module Commands
- **GF.ADD**: Add points to geofence indexes
- **GF.PADD**: Add polygons to geofence indexes
- **GF.SEARCH**: Advanced spatial searches (WITHIN, CONTAINS, INTERSECTS)
- **GF.CLUSTER**: Cluster points using GEOHASH or KMEANS algorithms
- Visual cluster representation with colored markers

#### Map - Polygon and Location selector / options to interact with valkey
![](https://github.com/KarthikSubbarao/geoplotter/blob/main/images/map.png?raw=true)

#### Results
![](https://github.com/KarthikSubbarao/geoplotter/blob/main/images/results.png?raw=true)

## Usage

1. **Drawing**: Use the drawing tools to add markers (points) and polygons
2. **Standard GEO**: Use the top buttons for traditional Valkey GEO operations
3. **Geofence**: Use the bottom section for advanced geofence operations:
   - Set an index name (default: gf_index)
   - Add points/polygons to geofence indexes
   - Perform spatial searches with different relationship types
   - Cluster points and visualize results with colored markers

Build and Startup Instructions on mac:
```
pyenv local 3.8.10

export PATH="$HOME/.pyenv/bin:$PATH"
if which pyenv > /dev/null; then
  eval "$(pyenv init --path)"
  eval "$(pyenv init -)"
fi
python --version

pip install -r requirements.txt

python ./web.py
```

Build and Startup Instructions on Ubuntu:
```
python3 -m venv venv
source venv/bin/activate
python --version

pip install -r requirements.txt

python ./web.py
```
