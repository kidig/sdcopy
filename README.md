# sdcopy

`sdcopy` is a command-line tool designed to copying files from your camera or any SD cards
into structured folders based on the last modified time.

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
destination = %Y-%m-%d/RAW Photos/

[Videos]
path = PRIVATE/M4ROOT/CLIP
destination = %Y-%m-%d/Videos/
```

* `path`: Specifies the relative path within the source directory where files are located.
* `destination`: Defines the destination folder structure using `strftime` format, like `%Y-%m-%d`, etc.

### Command-line Options

Usage: `sdcopy [OPTIONS] [SOURCE]... DEST`

* `SOURCE`: Source directory/directories from which files will be copied.
* `DEST`: Destination directory where organized files will be copied. It accepts `strftime` format: `%Y-%m-%d`
* `-c, --config`: Path to the configuration file (default: `config.ini`, `~/.sdcopy.ini`).
* `--dry-run`: Perform a trial run without making changes.
* `--threads`: Number of concurrent thread for file copying (default: 4).

Example command: copying files into separate folders by file modified time and `YYYY-MM-DD` format 
```bash
sdcopy /path/to/source /path/to/destination/%Y-%m-%d/ -c config.ini"
```

## License

sdcopy is licensed under the MIT License. See the `LICENSE` file for details.
