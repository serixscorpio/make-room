# Development

Clone this repository.

Create a virtual environment, for example, directory `venv` using Python's `venv` module.
```
python -m venv venv
```

Activate the new environment with:
```
source ./venv/bin/activate
```

Make sure the latest pip version is in your virtual environment:
```
pip install --upgrade pip
```

Install all dependencies:
```
pip install -e ".[test,dev]"
```

Test run cli tool:
```
make-room --help
```

# Usage

To run the `make_room.py` script:

```sh
# at project root
hatch run make-room ~/ec-keep/photos-videos/2023/
```

This finds video within the `~/ec-keep/photos-videos/2023/` directory and encodes them using H265 with a constant rate factor of 28.
