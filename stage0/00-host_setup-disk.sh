#!/bin/bash
set -e
set -x

source ./util.sh

if [[ "$OUTPUT_DEVICE" =~ ^/dev/loop ]]; then
  info "Creating disk image"
  fallocate -l "$IMAGE_OUTPUT_SIZE" "$IMAGE_OUTPUT_PATH"
else
  info "Zeroing the beginning of the SD card"
  dd if=/dev/zero of="$OUTPUT_DEVICE" bs=1M count=8
fi

info "Partitioning disk image"
(
  echo o # create a new MS-DOS partition table

  # TODO: Secondary system partition for AB

  # Boot partition
  echo n     # new partition
  echo p     # primary partition
  echo 1     # partition number
  echo 4096  # first sector (accept default)
  echo +200M # last sector
  echo t     # change partition type
  echo 0b    # W95 FAT32 (LBA)

  # Root filesystem
  echo n      # new partition
  echo p      # primary partition
  echo 2      # partition number
  echo 413696 # first sector at 200M + 4096
  echo        # last sector (accept default)

  echo w # write changes
) | /sbin/fdisk "$IMAGE_OUTPUT_PATH" > /dev/null

if [[ "$OUTPUT_DEVICE" =~ ^/dev/loop ]]; then
  info "Setting up loop device"
  losetup -P "$OUTPUT_DEVICE" "$IMAGE_OUTPUT_PATH"
  boot_part="${OUTPUT_DEVICE}p1"
  root_part="${OUTPUT_DEVICE}p2"
else
  boot_part="${OUTPUT_DEVICE}1"
  root_part="${OUTPUT_DEVICE}2"
fi

file "$OUTPUT_DEVICE"
file "$boot_part"
file "$root_part"
ls -l "$OUTPUT_DEVICE"*

info "Creating boot filesystem"
mkfs.vfat -F 32 "$boot_part"

info "Creating root filesystem"
mkfs.ext4 -q "$root_part"

mkdir -p "$BUILD_DIR"

info "Mounting root partition"
mount -t ext4 -o rw,defaults,noatime "$root_part" "$BUILD_DIR"

info "Mounting boot partition"
mkdir -p "$BUILD_DIR/boot"
mount -t vfat -o rw,defaults,noatime "$boot_part" "$BUILD_DIR/boot"
