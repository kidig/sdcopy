import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path

import click

DEFAULT_CFG = [
    "config.ini",
    Path.home() / ".sdcopy",
]


def file_times(src: Path) -> tuple[float, float]:
    """Get file timestamps"""
    stat = src.stat()
    return stat.st_atime, stat.st_mtime


def copy_file(src: Path, dst: Path, dry_run: bool = False) -> None:
    click.echo(f"copying {src.name} -> {dst}")
    if not dry_run:
        os.makedirs(dst.parent, exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy(src, dst)
            os.utime(dst, times=file_times(src))
            click.echo(f"{src.name} done.")
        else:
            click.echo(f"{src.name} already exists.")
    else:
        click.echo(f"{src.name} done.")


def create_default_config(cfg: ConfigParser, section: str = "Default") -> None:
    cfg.add_section(section)
    cfg.set(section, "path", "")
    cfg.set(section, "format", "")


@click.command()
@click.argument("source", nargs=-1, type=click.Path(exists=True))
@click.argument("dest", nargs=1, type=click.Path())
@click.option("-c", "--config", type=click.Path(dir_okay=False))
@click.option("--dry-run", is_flag=True)
@click.option("--threads", default=4)
def main(source, dest, config, dry_run, threads) -> None:
    dst_path = Path(dest)

    cfg = ConfigParser(interpolation=None)
    if not config:
        config = DEFAULT_CFG

    if dry_run:
        click.echo("Dry-run mode is ENABLED")

    if config_exists := cfg.read(config):
        click.echo(f"Config loaded: {config_exists}")
    else:
        create_default_config(cfg)

    with ThreadPoolExecutor(threads) as t:
        for section in cfg.sections():
            folder = cfg[section]
            if "path" not in folder:
                continue

            folder_fmt = folder.get("destination")

            for src_folder in source:
                src_path = Path(src_folder) / folder["path"]
                click.echo(f"== {section} [{src_path}] ==")

                if not src_path.is_dir():
                    click.echo(f"f{src_path} not found!")
                    continue

                for src_file in src_path.iterdir():
                    if src_file.is_dir():
                        continue

                    src_file_mtime = datetime.fromtimestamp(src_file.stat().st_mtime)
                    dst_path_resolved = Path(src_file_mtime.strftime(str(dst_path)))
                    dst_file = dst_path_resolved / Path(src_file_mtime.strftime(str(folder_fmt))) / src_file.name
                    t.submit(copy_file, src_file, dst_file, dry_run)

    if dry_run:
        click.echo("Dry-run mode. NO CHANGES MADE")

    click.echo("Done")


if __name__ == "__main__":
    main()
