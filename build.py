#!/usr/bin/env python3
import argparse
import atexit
import os
import re
import subprocess
import sys
from pathlib import Path
from shutil import copytree, rmtree
from typing import List

REPO_DIR = Path(__file__).absolute().parent
IMAGE_OUTPUT_SIZE = "8G"
# Either a block device or disk image file
OUTPUT_DEVICE = subprocess.check_output(['losetup', '-f']).decode().strip()
IS_BLOCK_DEVICE = True
STAGE_REGEX = re.compile("^stage([0-9]+)$")
PROC_MOUNTS = Path("/proc/mounts")


def detect_available_platforms() -> List[str]:
    """Detect stage0 platforms that are available."""
    platforms_dir = REPO_DIR / "platforms"
    return [platform.name for platform in platforms_dir.iterdir()]


def cleanup(build_dir):
    print("Syncing disks")
    os.sync()
    print("Unmounting")
    subprocess.run(
        ["umount", "--recursive", build_dir],
    )
    if not IS_BLOCK_DEVICE:
        subprocess.run(
            ["losetup", "-d", OUTPUT_DEVICE],
        )


def determine_stage_list() -> List[Path]:
    return sorted(REPO_DIR.glob("stage*"))


def run_stage(stage: Path, environment, build_dir):
    stage_path = build_dir / "stage"
    for i in [str(x).zfill(2) for x in range(100)]:

        for run_script in stage.glob(f"{i}-host_*.sh"):
            subprocess.run(
                [str(run_script)],
                cwd=REPO_DIR,
                env=environment,
            )

        for run_script in stage.glob(f"{i}-chroot_*.sh"):
            copytree(stage, stage_path)
            subprocess.run(
                ["arch-chroot", str(args.build_dir), f"/stage/{run_script.name}"],
                cwd=REPO_DIR,
                env=environment,
            )
            rmtree(stage_path)

        for run_script in stage.glob(f"{i}-packages*"):
            subprocess.run(
                ["arch-chroot", str(args.build_dir), "pacman", "-S", "--noconfirm"]
                + run_script.open("r").read().splitlines(),
                cwd=REPO_DIR,
                env=environment,
            )


if __name__ == "__main__":
    if os.geteuid() != 0:
        sys.stderr.write("This script must run as superuser.\n")
        sys.exit(1)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--build-dir",
        help="build directory",
        type=Path,
        default=REPO_DIR / "mnt",
    )
    parser.add_argument(
        "-c",
        "--cache-dir",
        help="cache directory",
        type=Path,
        default=REPO_DIR / "cache",
    )
    parser.add_argument(
        "platform",
        help="platform to build image for",
        choices=detect_available_platforms(),
        type=str,
    )
    parser.add_argument(
        "output_file",
        help="file to write image to",
        type=Path,
    )
    args = parser.parse_args()

    print("SR Image Builder")
    print(f"Build directory: {args.build_dir}")
    Path(args.build_dir).mkdir(parents=True, exist_ok=True)

    stages = determine_stage_list()

    if args.output_file.is_block_device():
        OUTPUT_DEVICE = str(args.output_file)

    existing_path = os.environ["PATH"]
    environment = {
        "OUTPUT_DEVICE": OUTPUT_DEVICE,
        "IMAGE_OUTPUT_SIZE": IMAGE_OUTPUT_SIZE,
        "IMAGE_OUTPUT_PATH": str(args.output_file),
        "BUILD_DIR": str(args.build_dir),
        "CACHE_DIR": str(args.cache_dir),
        "PLATFORM": args.platform,
    }

    atexit.register(cleanup, args.build_dir)

    for stage in stages:
        run_stage(stage, environment, args.build_dir)
