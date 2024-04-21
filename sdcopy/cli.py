import argparse
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path

DEFAULT_CFG = [
    "config.ini",
    Path.home() / ".sdcopy",
]


def file_times(src: Path) -> tuple[float, float]:
    """Get file timestamps"""
    stat = src.stat()
    return stat.st_atime, stat.st_mtime


def copy_file(src: Path, dst: Path, dry_run: bool = False) -> None:
    print(f"{src.name} > {dst} ", end="")

    if not dry_run:
        os.makedirs(dst.parent, exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy(src, dst)
            os.utime(dst, times=file_times(src))
            print("[done]")
        else:
            print("[already exists]")

    else:
        print("[done]")


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

    if args.dry_run:
        print("Dry-run mode is ENABLED")

    dst_path = Path(args.dest)

    config = args.config
    if not config:
        config = DEFAULT_CFG

    cfg = ConfigParser(interpolation=None)

    if config_exists := cfg.read(config):
        print(f"Config loaded: {config_exists}")
    else:
        create_default_config(cfg)

    with ThreadPoolExecutor(args.threads) as t:
        for section in cfg.sections():
            folder = cfg[section]
            if "path" not in folder:
                continue

            folder_fmt = folder.get("destination")

            src_path = Path(args.source) / folder["path"]
            print(f"\n{section} [{src_path}]")

            if not src_path.is_dir():
                print(f"f{src_path} not found!")
                continue

            for src_file in src_path.iterdir():
                if src_file.is_dir():
                    continue

                src_file_mtime = datetime.fromtimestamp(src_file.stat().st_mtime)
                dst_path_resolved = Path(src_file_mtime.strftime(str(dst_path)))
                dst_file = dst_path_resolved / Path(src_file_mtime.strftime(str(folder_fmt))) / src_file.name
                t.submit(copy_file, src_file, dst_file, args.dry_run)

    if args.dry_run:
        print("Dry-run mode. NO CHANGES MADE")

    print("Done")


if __name__ == "__main__":
    main()
