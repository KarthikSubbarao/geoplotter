# geoplotter
Geo Coord Visualizer of Locations and Polygons Boundaries that interacts with Valkey.

It uses GEO commands from Valkey to add, retrieve, and search using geo coordinates.

#### Map - Polygon and Location selector / options to interact with valkey
![](https://github.com/KarthikSubbarao/geoplotter/blob/main/images/map.png?raw=true)

#### Results
![](https://github.com/KarthikSubbarao/geoplotter/blob/main/images/results.png?raw=true)

Build and Startup Instructions:
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
