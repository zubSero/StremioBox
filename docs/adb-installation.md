# ADB updates and installation

[Installation guide](installation.md) · [Hardware](hardware.md) · [Security](../SECURITY.md)

ADB can update apps without a USB installer. A full operating-system installation over ADB requires additional support for the device's disk and boot layout.

| Starting point | Available route | Status |
| --- | --- | --- |
| Initial StremioBox image with Dutch Home | Install the signed English Home APK over ADB | Tested on the physical NUC, including persistence after reboot |
| Existing StremioBox needing a native platform update | Root-ADB system updater with compatible disk/boot layout | Technically possible; used during development, but a portable public updater is not released |
| Another Android TV distribution | Inspect root access, partitions, bootloader and data compatibility before migration | No general migration installer is available |
| New PC or an installation without root-ADB access | Boot the StremioBox USB image | Use the [installation guide](installation.md); disk-installer validation remains pending |

The current English Home release changes only the Home APK against the initial public image. Existing StremioBox users can apply that interface update through the tested route below. This does not replace the installed system image or change its recorded image identity.

## Update Home without Python

You need Google's [standalone SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools), which includes ADB. Android Studio and Python are not required. Download and extract the package for your computer.

Download [StremioBoxHome-1.1-en.apk](https://github.com/zubSero/StremioBox/releases/download/r6/StremioBoxHome-1.1-en.apk) and place it in the extracted `platform-tools` folder. Open a terminal in that folder.

### 1. Verify the APK

Expected SHA-256:

```text
088d354170bb5029dfcde96047115f8881893c47831379d7a398e9efb599d6ec
```

Windows PowerShell:

```powershell
Get-FileHash .\StremioBoxHome-1.1-en.apk -Algorithm SHA256
```

Linux:

```sh
sha256sum StremioBoxHome-1.1-en.apk
```

macOS:

```sh
shasum -a 256 StremioBoxHome-1.1-en.apk
```

Proceed only if the hash matches. The APK is signed with the original Home release certificate.

### 2. Connect and authorize

Find the box's local address in Android's network settings. StremioBox starts authenticated ADB on TCP 5555. Use a trusted local network and approve your own computer on the TV when prompted.

On Windows, replace `YOUR_BOX_ADDRESS` with the address shown on your box:

```powershell
.\adb.exe connect YOUR_BOX_ADDRESS:5555
.\adb.exe devices
```

On Linux/macOS use `./adb` instead of `.\adb.exe`. The selected device must show `device`, not `unauthorized` or `offline`.

### 3. Install on the selected box

Use the explicit device selector so another connected Android device is not updated accidentally:

```powershell
.\adb.exe -s YOUR_BOX_ADDRESS:5555 shell pm path local.stremiobox.home
.\adb.exe -s YOUR_BOX_ADDRESS:5555 install -r .\StremioBoxHome-1.1-en.apk
```

Linux/macOS:

```sh
./adb connect YOUR_BOX_ADDRESS:5555
./adb devices
./adb -s YOUR_BOX_ADDRESS:5555 shell pm path local.stremiobox.home
./adb -s YOUR_BOX_ADDRESS:5555 install -r ./StremioBoxHome-1.1-en.apk
```

The first command should return the existing StremioBox Home package path. If it does not, stop: this is an update for an existing compatible StremioBox installation. The install command should finish with `Success`. Open Home to see the English interface; an immediate reboot is not required.

If Android reports a signing mismatch, do not uninstall Home to force the update. A differently signed fork needs its own compatible update package. Existing app data is retained by the normal `install -r` update.

## Full system installation through ADB

During development, root-ADB deployed verified kernel, initrd, system and recovery payloads into an isolated installation directory and updated the NUC's GRUB boot selection. The previous working installation was retained as a recovery choice. This established that the method works on that NUC; the private deployment scripts checked its exact disk identifiers and boot configuration.

A public installer must replace those workstation-specific assumptions with verified support for the actual target. Before it writes anything, it needs to check:

- Root shell access, supported computer/product and available storage.
- The mounted installation partition, installation directory and GRUB/UEFI boot configuration.
- Current payload hashes and compatibility with the selected update.
- A verified package containing all required boot and system files.
- Separate staging, an intact previous installation and a tested recovery path if boot fails.

Migrating another Android distribution also needs a decision about keeping or isolating user data. Copying Android data across major versions is not a validated migration route here.

**The release ISO is not an Android recovery OTA package.** `adb install` installs APKs; `adb sideload` requires an update package supported by the target's recovery. Neither command installs this ISO as a complete operating system. A recovery update ZIP or the dedicated root-ADB installer needs its own build and validation. See [Android's OTA documentation](https://source.android.com/docs/core/ota/nonab) and [ADB documentation](https://developer.android.com/tools/adb).

Until that installer is published, use the tested Home update above for existing StremioBox devices and the USB path for a fresh system. The [roadmap](roadmap.md) tracks the portable full-system updater.
