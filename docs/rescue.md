# Rescue system

[Project](../README.md) · [Troubleshooting](troubleshooting.md) · [Kit sources](../rescue/README.txt)

The optional **StremioBox rescue kit** adds a small Alpine Linux system to the EFI partition. It starts from the boot menu, runs entirely from RAM and leaves the Android partition unmounted until you ask for it. Use it when Android no longer reaches the Home screen: check the file system, copy logs, restore a backup or undo a change, over SSH or on the TV with a USB keyboard.

The kit is a separate download on the [r7 release page](https://github.com/zubSero/StremioBox/releases/tag/r7) (`StremioBox-rescue-kit-r7.zip`, about 40 MB). It is not installed by default.

## What is inside

| File | Purpose |
| --- | --- |
| `kernel` | The StremioBox kernel, byte-identical to the ISO's `/kernel` |
| `rescue.img` | Alpine 3.24 userland with e2fsprogs, dosfstools, dropbear SSH, Wi-Fi tools and the NUC's Ethernet/Wi-Fi drivers |
| `enable-rescue.sh` | Copies the kit to the EFI partition and adds one GRUB entry; `--remove` undoes both |
| `authorized_keys` | Put your SSH public key here before installing |
| `wifi.conf.example` | Optional Wi-Fi settings for the rescue system |
| `package-versions.txt` | Exact Alpine package versions for license and source lookup |

The kit contains **no SSH keys and no passwords**. SSH starts only when your own public key is present on the EFI partition, and password logins are always refused. A device-specific SSH host key is generated on the first rescue start and stored next to the kit, so its fingerprint stays the same afterwards.

## Install

You need ADB access to the box (see the [ADB guide](adb-installation.md)) and a computer with an SSH client.

1. Extract the ZIP. Optionally paste your SSH public key (for example the contents of `~/.ssh/id_ed25519.pub`) into `authorized_keys`.
2. Run from the folder that contains the extracted `StremioBox-rescue-kit` directory:

   ```sh
   adb connect <box-address>:5555
   adb root
   adb push StremioBox-rescue-kit /data/local/tmp/
   adb shell sh /data/local/tmp/StremioBox-rescue-kit/enable-rescue.sh
   ```

3. The script verifies the kit's checksums and the free space, finds the EFI partition that holds the StremioBox GRUB configuration, keeps a backup as `grub.cfg.before-rescue` and adds the entry **StremioBox rescue system**. Running it again changes nothing.

If no matching GRUB configuration is found, the script stops without changing anything. Then add the entry yourself:

```text
menuentry 'StremioBox rescue system' --id stremiobox-rescue {
    search --no-floppy --file --set=root /efi/rescue/rescue.img
    linux /efi/rescue/kernel quiet loglevel=3 panic=10
    initrd /efi/rescue/rescue.img
}
```

To remove the kit: `adb shell sh /data/local/tmp/StremioBox-rescue-kit/enable-rescue.sh --remove`.

## Use

Restart and pick **StremioBox rescue system** in the boot menu. If the menu is hidden, hold **Esc** or **Shift** during start-up. The TV shows the rescue system's IP address and SSH host key fingerprint.

```sh
ssh root@<box-address>
```

| Command | What it does |
| --- | --- |
| `sb-disk` | Runs `e2fsck -p` on the Android partition and mounts it read-write on `/mnt/android`; finds it automatically or takes a device such as `/dev/nvme0n1p2` |
| `sb-android` | Unmounts and restarts into the default entry (StremioBox) |
| `/mnt/esp` | The EFI partition, including the GRUB configuration and `efi/rescue` |
| Alt+F2 | Local root shell on the TV; physical access is trusted |

Without any login the rescue system restarts into Android after 15 minutes, so a box that was started into rescue by accident recovers on its own. Ethernet uses DHCP. For Wi-Fi, copy `wifi.conf.example` to `efi/rescue/wifi.conf` on the EFI partition and fill in your network.

## Tested

| Check | Result |
| --- | --- |
| Boot of the kit in QEMU/KVM with an NVMe disk and Intel e1000e network | DHCP, SSH with key, password login refused, `sb-disk` found and mounted the Android partition |
| Second start | Host key reused from the EFI partition |
| `enable-rescue.sh` in a fresh r7 Android guest | Kit copied, GRUB entry added once, re-run idempotent, `--remove` restores the original `grub.cfg` |
| Boot through the added GRUB entry under UEFI | Rescue started from the EFI partition and accepted the installed key |
| Development NUC10i5FNH | A private build of the same design runs there, including recovery after two failed Android starts |

**Test boundary:** the public kit has not yet been installed on a physical NUC that was set up with the r7 disk installer. The automatic switch to rescue after failed starts exists only on the development NUC; the public kit is started from the menu.

## Build it yourself

[`tools/build_rescue.sh`](../tools/build_rescue.sh) builds the kit on a Linux x86_64 host from the pinned Alpine 3.24.2 minirootfs (SHA-256 checked), the [package list](../rescue/packages.txt), the [scripts](../rescue/root/) and the kernel, network modules and Wi-Fi firmware taken from a verified StremioBox ISO:

```sh
sudo tools/build_rescue.sh alpine-minirootfs-3.24.2-x86_64.tar.gz StremioBox-Android16-r7-nuc10_tv.iso out/
```

Alpine packages are downloaded during the build, so a later build can include newer package revisions and will not be byte-identical. `package-versions.txt` records the exact versions in each kit.
