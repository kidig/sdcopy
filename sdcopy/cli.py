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


def format_path(src: Path, fmt: str) -> str:
    """Format path pattern"""
    mtime = datetime.fromtimestamp(src.stat().st_mtime)
    return fmt.format(
        year=mtime.year,
        month=str(mtime.month).zfill(2),
        day=str(mtime.day).zfill(2),
    )


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


@click.command()
@click.argument("source", nargs=-1, type=click.Path(exists=True))
@click.argument("dest", nargs=1, type=click.Path())
@click.option("-c", "--config", type=click.Path(dir_okay=False))
@click.option("-df", "--dest-format", default="{year}-{month}-{day}")
@click.option("--dry-run", is_flag=True)
@click.option("--threads", default=4)
def main(source, dest, config, dest_format, dry_run, threads) -> None:
    dst_path = Path(dest)

    cfg = ConfigParser()
    if not config:
        config = DEFAULT_CFG

    config_exists = cfg.read(config)

    if dry_run:
        click.echo("Dry-run mode is ENABLED")
    else:
        os.makedirs(dest, exist_ok=True)

    with ThreadPoolExecutor(threads) as t:
        if config_exists:
            click.echo(f"Config loaded: {config_exists}")

            for section in cfg.sections():
                folder = cfg[section]
                if "path" not in folder:
                    continue

                folder_format = folder.get("format", dest_format)

                for src_folder in source:
                    src_path = Path(src_folder) / folder["path"]
                    click.echo(f"== {section} [{src_path}] ==")

                    if not src_path.is_dir():
                        click.echo(f"{src_path} not found!")
                        continue

                    for src_file in src_path.iterdir():
                        if src_file.is_dir():
                            continue

                        dst_file = dst_path / format_path(src_file, folder_format) / src_file.name
                        t.submit(copy_file, src_file, dst_file, dry_run)

        else:
            for src_folder in source:
                src_path = Path(src_folder)
                for src_file in src_path.iterdir():
                    dst_file = dst_path / format_path(src_file, dest_format) / src_file.name
                    t.submit(copy_file, src_file, dst_file, dry_run=dry_run)

    if dry_run:
        click.echo("Dry-run mode. NO CHANGES MADE")

    click.echo("Done")


if __name__ == "__main__":
    main()
