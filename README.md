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

# `make_room` Usage

```sh
# at project root
python make-room ~/ec-keep/photos-videos/2023/
```

This finds video within the `~/ec-keep/photos-videos/2023/` directory and encodes them using H265 with a constant rate factor of 28.

# `to_avif` Usage

```sh
# at project root
python src/make_room/to_avif.py ~/ec-keep/photos-videos/2023/
```

This finds jpeg pictures within the `~/ec-keep/photos-video/2023/` direcotry and encodes them to [avif](https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Image_types#avif_image) format, which has better compression (i.e. saves space).
