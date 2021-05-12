# SR Robot Base System

[![Image Build](https://github.com/srobo/robot-base/actions/workflows/image.yml/badge.svg)](https://github.com/srobo/robot-base/actions/workflows/image.yml)
[![Lint](https://github.com/srobo/robot-base/actions/workflows/shellcheck.yml/badge.svg)](https://github.com/srobo/robot-base/actions/workflows/shellcheck.yml)

Scripts used to create a system image for SR brain board SD cards.

**Supported Platforms:**

| Platform            | Status    |
|---------------------|-----------|
| ODroid U3           | Supported |
| Raspberry Pi 3B/B+  | Supported |
| Raspberry Pi 4B/400 | Supported |

## Requirements

- bash
- Python 3.8 or newer
- fdisk
- [arch-install-scripts](https://archlinux.org/packages/extra/any/arch-install-scripts/)
- [archlinuxarm-keyring](http://mirror.archlinuxarm.org/armv6h/core/archlinuxarm-keyring-20140119-1-any.pkg.tar.xz)
- [uboot-tools](https://archlinux.org/packages/extra/any/uboot-tools/)

You will also need to be running a system which is either running on an ARM platform (armv7 or newer) or have `binfmt_misc` set up on your system. 

You can do this on arch by installing the [qemu-user-static-bin AUR package](https://aur.archlinux.org/packages/qemu-user-static-bin/)

If you would like to run this under Docker, you can do so using [multiarch/qemu-user-static](https://github.com/multiarch/qemu-user-static).

## Stages

The build process loops through a number of stages to gradually build up the image in a modular style.

The stages each have a distinct purpose:

- Stage 0 - Build working ALARM system for device
- Stage 1 - Minimal SR Kit Software
- Stage 2 - SR Development Image

Stage 0 will be different for each hardware category

There are three types of files in each stage:

- `xx-host_*.sh` - Run the bash script on the build host
- `xx-chroot_*.sh` - Run the bash script inside the chroot
- `xx-packages` - Install these packages inside the chroot

The files are executed by sorting them on the number at the start. It should be
assumed that any file starting with the same number may be executed in parallel
within the same stage.
