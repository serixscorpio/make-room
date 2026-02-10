**1. Consolidate Scripts:**

*   Merge the functionality of `make_room.py` and `to_avif.py` into a single, unified script. This will reduce code duplication and make the tool easier to use and maintain. The new script will be intelligent enough to determine whether to convert a file to h265 (for videos) or AVIF (for images) based on the file type.

**2. Enhance the Command-Line Interface (CLI):**

*   The new, unified script will have a more powerful and flexible CLI.
*   A `--recursive` option will be added to allow for recursive traversal of directories. This will be on by default.
*   A `--target-data-size` option will be added to allow you to specify the maximum amount of data to process. This will default to 3GB.

**3. Improve the `README.md`:**

*   The `README.md` file will be updated to reflect the new, unified CLI.
*   Clear and concise usage examples will be provided to demonstrate how to use the new features.
