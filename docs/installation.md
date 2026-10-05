# Install StremioBox r6

[Back to the project](../README.md) · [Hardware](hardware.md) · [Troubleshooting](troubleshooting.md)

r6 targets the Intel NUC10i5FNH. Have a USB keyboard available for firmware menus and initial setup. The Homatics remote can be paired after Android starts.

## 1. Download and verify

Clone this repository, then use Python 3.10 or newer:

```sh
python3 tools/download.py --output downloads
```

Windows:

```powershell
py tools/download.py --output downloads
# Or, from the same checkout:
powershell -File tools/download.ps1 -OutputDirectory downloads
```

The ISO is distributed as `.iso.001` and `.iso.002`. These are sequential raw pieces, not two bootable images and not a ZIP archive. The helper validates each piece and the reconstructed ISO against the [r6 manifest](../releases/r6.json). It keeps verified parts so rerunning can reuse them; an interrupted part restarts its own transfer. Existing unrelated output is never overwritten.

If you downloaded the two pieces yourself, put them together in a folder and run:

```sh
python3 tools/download.py --output downloads --offline
```

Expect about 6 GB free while parts and the final image coexist. After a successful verification you can remove the two part files yourself. Keep the ISO and its hash.

```text
StremioBox-Android16-r6-nuc10_tv.iso
2,874,343,424 bytes
SHA-256: f5e8642165e732c0a44dac4a87a36e56b297ed3e1c928f39d2f4dec8e1783550
```

Checksums detect corruption and bind the pieces to this release; they are not a separate publisher signature. Always obtain the script and manifest from this project's repository or release.

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

## English Home update for an existing r5 box

The r6 image includes English Home 1.1. If you already installed r5, the signed `StremioBoxHome-1.1-en.apk` release asset updates only Home, without replacing the native platform. With your authorized ADB connection:

```sh
adb install -r StremioBoxHome-1.1-en.apk
```

The update uses the same release certificate and survives reboot. Installing Home alone does not add the Android/HDR fixes to a different OS. The historical r5 ISO retains its original Dutch Home 1.0; choose r6 for a fresh English installation.
