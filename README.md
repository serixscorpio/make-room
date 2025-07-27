# make-room

`make-room` is a command-line tool that helps you save space by converting your pictures and videos to more space-efficient formats. It can convert:

*   **Videos** to h265
*   **JPEG images** to AVIF

## Installation

1.  **Clone this repository:**

    ```bash
    git clone https://github.com/your-username/make-room.git
    cd make-room
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -e ".[test,dev]"
    ```

## Usage

To use `make-room`, simply run the `make-room` command with the path to the directory or file you want to convert:

```bash
make-room /path/to/your/media
```

By default, `make-room` will recursively search for videos and JPEG images in the specified directory and convert them. You can customize the behavior of the tool with the following options:

*   `--dry-run`: List the files that would be converted without actually performing the conversion.
*   `--no-recursive`: Only process files in the specified directory, not in subdirectories.
*   `--target-data-size`: Set a limit on the total amount of data to process, in bytes. The default is 3GB.

### Examples

*   **Convert all media in a directory and its subdirectories:**

    ```bash
    make-room /path/to/your/media
    ```

*   **Do a dry run to see what would be converted:**

    ```bash
    make-room --dry-run /path/to/your/media
    ```

*   **Convert only the files in the current directory:**

    ```bash
    make-room --no-recursive .
    ```

*   **Convert up to 1GB of media:**

    ```bash
    make-room --target-data-size 1000000000 /path/to/your/media
    ```

## Contributing

Contributions are welcome! If you have any ideas for how to improve `make-room`, please open an issue or submit a pull request.

## License

`make-room` is licensed under the MIT License.
