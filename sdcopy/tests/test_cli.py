import os
import subprocess
import tempfile
from datetime import datetime


def assert_copied_files(source: str, dest: str, files: list, destinations: list, cli_args: list | None = None):
    with tempfile.TemporaryDirectory() as tmpdir:
        # create source files
        source_files = []

        for filename, modified_time in files:
            source_file = os.path.join(tmpdir, filename)
            source_files.append(source_file)
            os.makedirs(os.path.dirname(source_file), exist_ok=True)

            with open(source_file, "w") as fp:
                fp.write("content")

            dt_mtime = datetime.strptime(modified_time, "%Y-%m-%d")
            os.utime(source_file, times=(int(dt_mtime.timestamp()), int(dt_mtime.timestamp())))

        # run sdcopy
        cmd = [
            "python",
            "sdcopy/cli.py",
            os.path.join(tmpdir, source),  # source
            os.path.join(tmpdir, dest),  # dest
        ]
        if cli_args:
            cmd += cli_args

        result = subprocess.run(cmd, capture_output=True, text=True)

        # check results
        assert result.returncode == 0, "cli failed"

        # check destinations
        expected = set([os.path.join(tmpdir, x) for x in destinations] + source_files)

        for root, dirs, filenames in os.walk(tmpdir):
            for name in filenames:
                dest_file = os.path.join(root, name)

                if dest_file not in expected:
                    assert False, f"{dest_file} not found"

                expected.remove(dest_file)

        for item in expected:
            assert False, f"{item} found"


def test_cli_simple_copy():
    files = [
        ("Sources/DSC08301.JPG", "2025-04-01"),
    ]
    destinations = [
        "Dest/DSC08301.JPG",
    ]
    assert_copied_files(
        "Sources/",
        "Dest/",
        files,
        destinations,
    )


def test_cli_dry_run():
    files = [
        ("Sources/DSC08301.JPG", "2025-04-01"),
    ]
    destinations = []
    assert_copied_files(
        "Sources/",
        "Dest/",
        files,
        destinations,
        ["--dry-run"],
    )


def test_cli_with_file_ext():
    files = [
        ("Sources/DSC08301.JPG", "2025-04-01"),
        ("Sources/DSC08301.ARW", "2025-04-01"),
    ]
    destinations = [
        "Dest/DSC08301.JPG",
    ]
    assert_copied_files(
        "Sources/",
        "Dest/",
        files,
        destinations,
        ["--ext", "jpg"],
    )


def test_cli_dest_with_date():
    files = [
        ("Sources/DSC08301.JPG", "2025-04-01"),
        ("Sources/DSC08302.JPG", "2025-04-02"),
    ]
    destinations = [
        "Dest/2025-04-01/DSC08301.JPG",
        "Dest/2025-04-02/DSC08302.JPG",
    ]
    assert_copied_files(
        "Sources/",
        "Dest/%Y-%m-%d/",
        files,
        destinations,
    )


def test_cli_dest_with_date_and_folder():
    files = [
        ("Sources/DSC08301.JPG", "2025-04-01"),
        ("Sources/DSC08302.JPG", "2025-04-02"),
    ]
    destinations = [
        "Dest/2025-04-01/Photos/DSC08301.JPG",
        "Dest/2025-04-02/Photos/DSC08302.JPG",
    ]
    assert_copied_files(
        "Sources/",
        "Dest/%Y-%m-%d/Photos/",
        files,
        destinations,
    )
