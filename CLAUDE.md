# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**make-room** is a CLI tool that saves disk space by converting media files to more efficient formats:
- Videos → H.265 (HEVC) codec via FFmpeg (CRF 23 quality threshold)
- JPEG images → AVIF format via Pillow (quality=70)

Built with Click for the CLI, managed with UV, requires Python >= 3.10.

## Common Commands

```bash
# Install dependencies
uv sync

# Run tests
bash scripts/test.sh        # runs: pytest tests

# Run linting
bash scripts/lint.sh         # runs: mypy src && ruff check src tests && ruff format --check src tests

# Run a single test
uv run pytest tests/test_make_room.py::test_make_room_on_file

# Run the CLI
uv run make-room /path/to/media [--dry-run] [--no-recursive] [--target-data-size BYTES]
```

## Architecture

The core logic lives in `src/make_room/make_room.py` (~180 lines). The `main()` Click command accepts a path (file or directory), walks it recursively, and dispatches each file to either `convert_to_h265()` (videos) or `jpeg_to_avif()` (JPEGs) based on MIME type detection via `python-magic`. Videos already encoded with CRF <= 23 are skipped. Converted files get a `-c` suffix (e.g., `video-c.mp4`); originals are not deleted.

`src/make_room/to_avif.py` is a legacy standalone script largely superseded by the consolidated logic in `make_room.py`.

## Code Style

- Ruff for linting and formatting (line length: 120)
- Enabled ruff rules: B, E, F, I, S, W
- Pre-commit hooks configured for ruff, trailing whitespace, large files, and config validation

## External Dependencies

FFmpeg must be installed on the system (used via `ffmpy` wrapper). Tests also require FFmpeg. The CI workflow installs it via `FedericoCarboni/setup-ffmpeg`.
