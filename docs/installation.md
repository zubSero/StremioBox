# Install StremioBox on an Intel NUC

[Back to the project](../README.md) · [Hardware](hardware.md) · [Troubleshooting](troubleshooting.md)

This guide covers **Intel NUC Preview — English Home**, tested on the Intel NUC10i5FNH. Its technical download identifier is `r6`. Have a USB keyboard available for firmware menus and initial setup; the Homatics remote can be paired after Android starts.

Already running StremioBox? The [ADB update guide](adb-installation.md) covers the tested English Home update without Python and explains the requirements for a full-system migration over ADB.

## Choose an installation route

| Situation | Start here |
| --- | --- |
| First installation, USB media available | Download the image below, then try live USB boot |
| Existing StremioBox with Dutch Home | [Update Home through ADB](adb-installation.md#update-home-without-python); no USB or Python needed |
| No USB stick | [USB-free options and their current status](without-usb.md) |

## 1. Download and verify without Python

Download and extract the [native download ZIP](https://github.com/zubSero/StremioBox/releases/download/r6/StremioBox-r6-native-download-1.1.zip). It is a small set of readable scripts, not an Android build toolchain. No Python installation is needed.

### Windows: double-click

1. Extract the ZIP completely; do not run it from inside the ZIP viewer.
2. Double-click **`Download-StremioBox.cmd`**.
3. Leave the window open until it says **ISO verified**. The image is in the extracted folder's `downloads` directory.

The launcher uses Windows' built-in PowerShell 5.1. It needs no administrator access and changes no permanent PowerShell policy; its execution-policy setting applies only to this process. Organization policies can still prevent scripts from running.

For a terminal or Git checkout, run from the folder containing `tools` and `releases`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/download.ps1 -OutputDirectory downloads
```

### Linux / macOS: system shell tools

```sh
bash tools/download.sh --output downloads
```

The helper uses Bash, curl and `sha256sum` (Linux) or `shasum` (macOS). Its output filesystem must support hard links, such as ext4 or APFS; use an ordinary local disk rather than FAT/exFAT. Windows PowerShell supports FAT/exFAT output too. The Windows and Linux paths have been exercised; a native macOS run is still pending.

### Already downloaded the pieces?

Put **both** release pieces in `downloads`, keeping their exact names. Use the same helper offline:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/download.ps1 -OutputDirectory downloads -Offline
```

```sh
bash tools/download.sh --output downloads --offline
```

The pieces are sequential raw bytes, not separate bootable images. Both helpers validate every existing piece before fetching missing ones, verify each download and check the final ISO independently. They reuse verified files, reject unrelated or corrupt existing files and publish the ISO only after verification. An interrupted part restarts its transfer when you rerun; completed valid parts are reused.

### Alternative: combine with 7-Zip

Download [part 1](https://github.com/zubSero/StremioBox/releases/download/r6/StremioBox-Android16-r6-nuc10_tv.iso.001) and [part 2](https://github.com/zubSero/StremioBox/releases/download/r6/StremioBox-Android16-r6-nuc10_tv.iso.002) into the same folder. With [7-Zip](https://7-zip.org/) installed, open PowerShell there and run:

```powershell
& "$env:ProgramFiles\7-Zip\7z.exe" x -tsplit -aos -oassembled StremioBox-Android16-r6-nuc10_tv.iso.001
Get-FileHash assembled\StremioBox-Android16-r6-nuc10_tv.iso -Algorithm SHA256
```

**Keep `-tsplit`:** it combines the pieces into an ISO. Automatic archive detection can instead open the ISO and extract its internal files. `-aos` skips an existing destination; use an empty `assembled` folder and compare the resulting hash below before using it. This command was tested with the actual release pieces and produced the original ISO hash. Unlike the native helper, this manual route requires you to compare the hash yourself.

### Storage and image identity

Expect about 6 GB free while parts and the final image coexist. After successful verification, you can remove the two part files yourself. Keep the ISO and its hash.

GitHub limits each release asset to under 2 GiB, so this 2.87 GB ISO is published in two pieces. A tested 7-Zip compression attempt produced a 2,195,182,200-byte archive, still above that limit. The native helpers assemble the pieces automatically; a single-file mirror remains on the [roadmap](roadmap.md). See [GitHub's release limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).

```text
StremioBox-Android16-r6-nuc10_tv.iso
2,874,343,424 bytes
SHA-256: f5e8642165e732c0a44dac4a87a36e56b297ed3e1c928f39d2f4dec8e1783550
```

The [JSON manifest](../releases/r6.json) and [shell manifest](../releases/r6-download.txt) record the same filenames, sizes and hashes; repository checks enforce that they agree. Checksums detect corruption and bind pieces to this release; they are not a separate publisher signature. Obtain scripts and manifests from this project.

The original Python helper remains an optional alternative for people who already have Python 3.10+: `python3 tools/download.py --output downloads` (Windows: `py tools/download.py --output downloads`). Downloading and assembling this release does not compile Android. A full [source build](building.md) still needs Android's Linux build dependencies, including Python.

## 2. Try a live boot first

Write the assembled ISO to a spare USB drive using an ISO-capable tool. Writing an image erases that USB drive. The hybrid image has BIOS and UEFI boot structures; the final fresh-data boot was tested through UEFI. Use the NUC's firmware boot menu to select the USB device.

Pick the **StremioBox live** option in the boot menu before choosing any disk installer. Complete Android setup, open Home and confirm picture, network, sound and remote pairing. This release is not Secure Boot certified; use the firmware settings appropriate for an unsigned community image.

## 3. Disk installation

Back up your existing OS and any data first. Choose the installer only when you have confirmed the target disk and understand that partitioning/formatting can erase it. This repository does not include a one-click disk-wiping script.

The distributed image's fresh-data UEFI live path was tested. **The destructive partition installer was not run against the live test NUC.** Treat a new disk installation as an additional validation step and retain recovery media. Existing installations that were upgraded manually during development do not constitute an installer certification.

Internal ISO labels such as `NUCTV_26278` are intentional: kernel root discovery depends on the matching label. Do not rename the volume label inside the ISO while rebranding it.

## 4. First start

- Finish Android setup and connect to your own network.
- Pair the Homatics B21 through Android's remote/accessory settings, using the remote's pairing procedure.
- Press Home to enter StremioBox Home. Open Stremio and sign in with your own account.
- The first-boot service installs the original, signed Stremio TV 1.10.4 x86_64 APK from the clean system image. It does not inject accounts, add-ons or personal data.
- Check the TV's HDR mode with suitable HDR10 material. A TV mode label alone does not certify every codec or HDR format.

## Maintenance access

This userdebug preview starts authenticated ADB on TCP 5555 after boot. With Android platform tools on a trusted local network:

```sh
adb connect <your-box-address>:5555
```

Authorize your own computer on the device when prompted. No developer key is shipped in the ISO. See [security and updates](../SECURITY.md) before exposing maintenance access to other networks.

<a id="update-an-existing-installation"></a>

## Update an existing installation

If your StremioBox uses the initial public image with Dutch Home, download the signed [English Home 1.1 APK](https://github.com/zubSero/StremioBox/releases/download/r6/StremioBoxHome-1.1-en.apk). Open a terminal in the folder containing it. With your authorized ADB connection:

```sh
adb install -r StremioBoxHome-1.1-en.apk
```

The update uses the same release certificate and survives reboot. It updates Home on the existing installation; it does not add the Android/HDR fixes to a different OS. New installations should use **Intel NUC Preview — English Home**, which already includes it. The historical Initial Release (`r5`) keeps Dutch Home 1.0. [Detailed changes](../CHANGELOG.md#english-home).

For Platform-Tools setup, APK verification and selection of the correct device, follow the [step-by-step ADB guide](adb-installation.md#update-home-without-python).
