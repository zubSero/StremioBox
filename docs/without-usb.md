# Installing without a USB stick

[Installation guide](installation.md) · [ADB updates](adb-installation.md)

The alternative depends on what can already boot on the computer. ADB needs a running Android system; it cannot reach a blank disk or a computer sitting in its firmware menu.

| What you already have | USB-free option | StremioBox status |
| --- | --- | --- |
| StremioBox with Dutch Home | Install the signed English Home APK over network ADB | Available and tested; [instructions](adb-installation.md#update-home-without-python) |
| Working Android with authorized root-ADB | Stage verified system/boot files and add a compatible boot entry | Used on the development NUC; a portable public migration installer is pending |
| Working Linux with administrator access | Prepare a separate installation directory/partition and a matching GRUB entry on the internal disk | Advanced integration path; no tested public StremioBox installer for this method |
| Blank disk, working wired network and another computer | PXE/network boot of an installation environment | NUC firmware supports network boot, but a StremioBox network-boot package and end-to-end test are pending |
| Windows only | Use external boot media, or wait for a supported internal-disk/network installer | No public Windows-to-StremioBox installation tool; an Android ADB client alone cannot install the OS |

## Existing Android: ADB

For the current English Home update, follow the [ADB guide](adb-installation.md). It requires Platform-Tools, not Python or Android Studio.

A full system migration requires **root** access as well as verified support for the installation partition and bootloader. A device appearing in `adb devices` establishes a connection; it does not establish permission to install a new operating system. Existing StremioBox, another LineageOS build and another Android TV distribution can have different layouts.

The development deployment kept the previous working installation and separate Android data as a recovery option. A public tool must implement that recovery behavior before this becomes a recommended installation route for other users.

## Existing Linux: internal-disk installation

A running Linux system can provide the file access and bootloader tools needed to prepare another OS without removable media. For StremioBox, the payload directory, data directory, filesystem and kernel arguments must match the image's initrd and GRUB setup. This needs a supported installation procedure and testing; simply copying the ISO to a disk is not an installation.

There is no published StremioBox command sequence for this route yet. Retain the existing OS and a recovery boot entry when developing it.

## Blank disk: network boot

[ASUS documents PXE boot on Intel NUC firmware](https://www.asus.com/us/support/faq/1052166/). It uses the wired network to obtain a boot environment from a configured server, typically another computer. It is separate from ADB and can work without Android already being installed.

Firmware support does not establish that the current StremioBox ISO boots over PXE. The server, bootloader, kernel/initrd and access to the system image must work together. We have not published or validated that setup. Do not treat the release ISO URL as a ready-made PXE installer.

## What is recommended today?

Use network ADB for the tested Home update on an existing StremioBox. For a first full installation, the USB live-boot path remains the documented entry point. Another compatible external boot device can serve the same purpose, but it also needs testing on your firmware.

If you need a first installation without removable media, provide the computer model, current OS and bootloader, available root/admin access, and whether wired network boot is available in a [setup discussion](https://github.com/zubSero/StremioBox/discussions). That information determines which integration can be built and tested. Do not post disk serial numbers, credentials or private device logs.
