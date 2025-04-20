import argparse
import logging
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import cast

DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL = os.getenv("SDCOPY_LOG_LEVEL", DEFAULT_LOG_LEVEL)
LOG_FORMAT = os.getenv("SDCOPY_LOG_FORMAT", "%(message)s")

log_level = logging.getLevelNamesMapping().get(LOG_LEVEL, DEFAULT_LOG_LEVEL)
logging.basicConfig(level=log_level, format=LOG_FORMAT)


class NoThreadPoolExecutor:
    def __init__(self, *args, **kwargs):
        pass

    def submit(self, fn, *args, **kwargs):
        fn(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def copy_file(source_file: str, dest_file: str, file_stat: os.stat_result, args: argparse.Namespace) -> None:
    if args.dry_run:
        logging.info("Copying %s -> %s in Dry-run mode", source_file, dest_file)
        return

    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    if not os.path.exists(dest_file):
        logging.info("Copying %s -> %s", source_file, dest_file)

        copy_start = time.perf_counter()
        shutil.copy(source_file, dest_file)
        os.utime(dest_file, times=(file_stat.st_atime, file_stat.st_mtime))
        logging.info("Finished copying %s in %.03f sec", dest_file, time.perf_counter() - copy_start)
    else:
        logging.info("File %s already exists", dest_file)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=str)
    parser.add_argument("dest", type=str)
    parser.add_argument("--ext", nargs="+", type=str)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--threads", type=int, default=1)

    args = parser.parse_args()
    time_start = time.perf_counter()
    num_threads = max(1, args.threads)

    if args.dry_run:
        logging.info("Dry-run mode is ENABLED")

    executor_cls = NoThreadPoolExecutor
    if num_threads > 1:
        executor_cls = ThreadPoolExecutor

    with executor_cls(num_threads) as t:
        for root, dirs, files in os.walk(args.source):
            for filename in files:
                source_file = cast(str, os.path.join(root, filename))

                if args.ext:
                    _, ext = os.path.splitext(filename)
                    if ext.removeprefix(".").lower() not in args.ext:
                        logging.info("%s skipped by extension", source_file)
                        continue

                file_stat = os.stat(source_file)
                source_mtime = datetime.fromtimestamp(file_stat.st_mtime)

                dest_path = source_mtime.strftime(args.dest)
                dest_file = cast(str, os.path.join(dest_path, filename))

                t.submit(copy_file, source_file, dest_file, file_stat, args)

    if args.dry_run:
        logging.info("Dry-run mode. NO CHANGES MADE")

    logging.info("Done in %.03f sec", time.perf_counter() - time_start)


if __name__ == "__main__":
    main()
