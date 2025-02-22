# geoplotter
Geo Coord Visualizer of Locations and Polygons Boundaries that interacts with Valkey

pyenv local 3.8.10

export PATH="$HOME/.pyenv/bin:$PATH"
if which pyenv > /dev/null; then
  eval "$(pyenv init --path)"
  eval "$(pyenv init -)"
fi
python --version   # Should say 3.8

pip install -r requirements.txt

python ./web.py 