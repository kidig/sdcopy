import argparse
import logging
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path

DEFAULT_CONFIG_PATHS = [
    "config.ini",
    Path.home() / ".sdcopy",
]
if default_config := os.getenv("SDCOPY_CONFIG"):
    DEFAULT_CONFIG_PATHS = [default_config]

DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL = os.getenv("SDCOPY_LOG_LEVEL", DEFAULT_LOG_LEVEL)
LOG_FORMAT = os.getenv("SDCOPY_LOG_FORMAT", "%(message)s")

log_level = logging.getLevelNamesMapping().get(LOG_LEVEL, DEFAULT_LOG_LEVEL)
logging.basicConfig(level=log_level, format=LOG_FORMAT)


def file_times(src: Path) -> tuple[float, float]:
    """Get file timestamps"""
    stat = src.stat()
    return stat.st_atime, stat.st_mtime


def copy_file(src: Path, dst: Path, dry_run: bool = False) -> None:
    if not dry_run:
        os.makedirs(dst.parent, exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy(src, dst)
            os.utime(dst, times=file_times(src))
            logging.info("%s -> %s is done", src.name, dst)
        else:
            logging.info("%s -> %s is already exists", src.name, dst)

    else:
        logging.info("%s -> %s is done", src.name, dst)


def create_default_config(cfg: ConfigParser, section: str = "Default") -> None:
    cfg.add_section(section)
    cfg.set(section, "path", "")
    cfg.set(section, "format", "")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=str)
    parser.add_argument("dest", type=str)
    parser.add_argument("-c", "--config")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--threads", type=int, default=4)

    args = parser.parse_args()
    time_start = time.perf_counter()

    if args.dry_run:
        logging.info("Dry-run mode is ENABLED")

    dst_path = Path(args.dest)

    config = args.config
    if not config:
        config = DEFAULT_CONFIG_PATHS

    cfg = ConfigParser(interpolation=None)

    if config_exists := cfg.read(config):
        logging.info(f"Config loaded: {config_exists}")
    else:
        create_default_config(cfg)

    threads = min(1, args.threads)
    for section in cfg.sections():
        folder = cfg[section]
        if "path" not in folder:
            continue

        folder_fmt = folder.get("destination")

        src_path = Path(args.source) / folder["path"]
        logging.info("[%s] from %s", section, src_path)

        if not src_path.is_dir():
            logging.warning("%s not found!", src_path)
            continue
        with ThreadPoolExecutor(threads) as t:
            for src_file in src_path.iterdir():
                if src_file.is_dir():
                    continue

                src_file_mtime = datetime.fromtimestamp(src_file.stat().st_mtime)
                dst_path_resolved = Path(src_file_mtime.strftime(str(dst_path)))
                dst_file = dst_path_resolved / Path(src_file_mtime.strftime(str(folder_fmt))) / src_file.name
                t.submit(copy_file, src_file, dst_file, args.dry_run)

    if args.dry_run:
        logging.info("Dry-run mode. NO CHANGES MADE")

    logging.debug("Done in %.02f sec", (time.perf_counter() - time_start) / 60)


if __name__ == "__main__":
    main()
