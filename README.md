# sdcopy - SD files organizer

`sdcopy` is a command-line tool designed to organize files from your camera or any SD card
into a structured archive based on their last modified times. 

The tool offers flexibility through a config file or command-line options,
allowing you to customize the destination folder structure and handle different type of files effectively.

## Features

- **Timestamp-based Organization**: Files are copied to the destination directory with folders 
  structured according to their modification timestamps.
- **Customizable Configuration**: Use INI file to define source paths, destination folder formats,
  and handle specific file types.
- **Concurrent Execution**: Utilized multithreading for faster file copying.
- **Dry-run Mode**: Preview the file organization without actually making changes.

## Installation

- Ensure you have Python 3.11.x installed
- Install project via pip: `pip install sdcopy`

## Usage

### Configuration File

Example configuration for a Sony camera:

```ini
[RAW Photos]
path = DCIM/100MSDCF
format = {year}-{month}-{day}/RAW Photos/

[Videos]
path = PRIVATE/M4ROOT/CLIP
format = {year}-{month}-{day}/Videos/
```

* `path`: Specifies the relative path within the source directory where files are located.
* `format`: Defines the destination folder structure using timestamp placeholders: `{year}`, `{month}`, and `{day}`.

### Command-line Options

Usage: `sdcopy [OPTIONS] [SOURCE]... DEST`

* `SOURCE`: Source directory/directories from which files will be copied.
* `DEST`: Destination directory where organized files will be copied.
* `-c, --config`: Path to the configuration file (default: `config.ini`, `~/.sdcopy.ini`).
* `--dest-format`: Custom format for the destination folder structure (default: `{year}-{month}-{day}`).
* `--dry-run`: Perform a trial run without making changes.
* `--threads`: Number of concurrent thread for file copying (default: 4).

Example command:
```bash
sdcopy /path/to/source /path/to/destination -c config.ini --dest-format="{year}-{month}-{day}"
```

## License

sdcopy is licensed under the MIT License. See the `LICENSE` file for details.