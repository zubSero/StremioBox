<div align="center">

![StremioBox](docs/assets/boot-screen.png)

# StremioBox

**Android 16 for an Intel NUC running Stremio on your TV.**

[![Intel NUC preview](https://img.shields.io/badge/download-Intel%20NUC%20preview-8b7bff?style=flat-square)](https://github.com/zubSero/StremioBox/releases/tag/r7)
[![Android 16](https://img.shields.io/badge/Android-16-65dfc1?style=flat-square&logo=android&logoColor=white)](docs/architecture.md)
[![Repository checks](https://github.com/zubSero/StremioBox/actions/workflows/validate.yml/badge.svg)](https://github.com/zubSero/StremioBox/actions/workflows/validate.yml)

[**Download**](https://github.com/zubSero/StremioBox/releases/tag/r7) · [**Installation**](docs/installation.md) · [**Changelog**](CHANGELOG.md) · [**Website**](https://zubsero.github.io/StremioBox/) · [**Nederlands**](README.nl.md)

</div>

StremioBox is a bootable Android TV system image based on Android 16 / LineageOS 23.2. It includes a remote-operated Home screen, Stremio TV 1.10.4 and fixes for Intel video output, HDMI audio, Bluetooth reconnection and subtitles. Playback uses Stremio's existing mpv interface, including its seek bar and player controls.

**This preview has been tested on one configuration: Intel NUC10i5FNH, Intel UHD graphics, Intel AX201 Bluetooth, a Homatics B21 remote and an LG HDR TV.** Other PCs and remotes need their own testing. The disk installer and long-duration playback tests are still pending; start with a live USB boot.

![StremioBox Home on the physical Intel NUC, with Aurora Store and Flicky under Apps & settings](docs/assets/home-r7-app-stores.png)

## What works on the tested NUC

| Feature | Observed result | Current limit |
| --- | --- | --- |
| 4K HDR10 video | HEVC Main10 uses Intel hardware decoding; the TV enters HDR mode with correct picture and audible sound | Tested around 24 fps in short samples; 4K60 and other HDR formats are unverified |
| Stremio controls | The existing mpv interface and seek bar remain available | VLC and ExoPlayer have not been validated |
| HDMI audio | Sound works before and after display standby | Receiver bitstream passthrough is unverified |
| Bluetooth remote | Ordinary Homatics keys work after reboot without repeating the pairing combination | The physical power-button cycle needs a separate retest |
| Display standby | Film picture, sound and remote control recover after Android sleep/wake commands | Long-standby hang fixed in r7; overnight physical retest pending; true S3 suspend unverified |
| Subtitles | External SRT subtitles follow Disabled, language selection and audio-track changes | Eight development regression cases; not every subtitle format |
| Home screen | English labels, D-pad navigation, Stremio, settings and installed apps | Home 1.1 was also checked after a physical reboot |
| App stores | Aurora Store and Flicky open from Home and survive reboot | Complete app installation through each store still to be tested; no Google Play services |

[Hardware details](docs/hardware.md) · [Test methods and results](docs/testing.md)

## New in this release — Standby & App Stores

- **No more hang after long standby.** The box could stay dark with No signal after hours of standby or an HDMI change. The fixed compositor is now in the image.
- **Aurora Store and Flicky** appear under **Apps & settings**, so you can install other apps. Stremio stays the main action. [App support](docs/standby-and-apps.md)
- **No scrolling console text** on the TV during standby.
- **Optional rescue system:** a boot-menu entry that starts a small Linux system from the EFI partition when Android no longer starts. SSH works only with your own key. [Rescue guide](docs/rescue.md)

The physical NUC runs the same changed files, but the overnight standby test and a reflash with the new ISO are still pending. [Test boundary](docs/testing.md#standby-and-app-stores-release)

## Download and try it

The current download is **Intel NUC Preview — Standby & App Stores**. It includes all earlier fixes, English Home 1.1, the standby fix and both app stores. [Read the changes](CHANGELOG.md#standby-and-app-stores).

1. Download the [native download ZIP](https://github.com/zubSero/StremioBox/releases/download/r7/StremioBox-r7-native-download.zip) and extract it.
2. **Windows:** double-click `Download-StremioBox.cmd`. **Linux/macOS:** open a terminal in the extracted folder and run `bash tools/download.sh --output downloads`. No Python is required.
3. Follow the [USB boot and installation guide](docs/installation.md). Allow about **6 GB free** for the download and assembled image.
4. After Android starts, pair your remote and sign in to Stremio with your own account. No accounts or add-ons are configured in the image.

The helper joins two download parts into one ISO and verifies their SHA-256 hashes. The resulting ISO is about **2.89 GB**. For manual downloads, source archives, the rescue kit and checksums, open the [release page](https://github.com/zubSero/StremioBox/releases/tag/r7).

**Already running r5 or r6?** Add the stores over ADB; the standby fix needs a reinstall with r7. [Update options](docs/installation.md#update-an-existing-installation).

**Already using the initial image with Dutch Home?** Install the [English Home update](docs/installation.md#update-an-existing-installation) to change the launcher language. It uses the same signing certificate and survives reboot.

[ADB update instructions without Python](docs/adb-installation.md) are available for existing installations. Full-system ADB migration requires supported root access and a compatible boot/disk layout; a portable system installer is still pending.

**No USB stick?** Read the [USB-free installation options](docs/without-usb.md), which distinguish the tested app update from system migration and network-boot work still needed.

<details>
<summary>Image filename and checksum</summary>

The release's technical identifier is `r7`; filenames and download URLs use it.

```text
StremioBox-Android16-r7-nuc10_tv.iso
2,886,336,512 bytes
SHA-256: 65b07feafd70670954231afc6a69a6b850445d67197c4d53f3c1cf1aff010bb8
```

[Download manifest](releases/r7.json) · [Image verification](releases/r7-image-verification.json) · [Image delta](releases/r7-image-delta.json)

</details>

## Before installing

- **Hardware scope:** Dolby Vision, HLG, AV1, 4K60, HDMI-CEC, other GPU families and subscription-service DRM certification are unverified. See the [compatibility matrix](docs/hardware.md).
- **Development security settings:** this is a userdebug image with permissive SELinux and authenticated ADB on TCP 5555. Use a trusted network. The shared image contains no personal ADB keys, accounts or Bluetooth bonds. [Security details](SECURITY.md).
- **Updates:** packaged fixes survive reboot. The tested same-version Stremio reinstall retained the integration; future app versions need compatibility review. There is no automatic OS update channel.

## Source, reports and development

**Pull requests are welcome.** Anyone can fork the project and submit fixes, hardware improvements, translations or documentation updates. You can open a PR directly; changes are reviewed before merging. [How to contribute](CONTRIBUTING.md).

| I want to… | Go to |
| --- | --- |
| See exactly what changed | [Detailed changelog](CHANGELOG.md) |
| Diagnose picture, audio or remote problems | [Troubleshooting](docs/troubleshooting.md) |
| Repair a box that no longer starts | [Rescue system](docs/rescue.md) |
| Report a bug or another hardware configuration | [Issues](https://github.com/zubSero/StremioBox/issues/new/choose) |
| Ask a setup question | [Discussions](https://github.com/zubSero/StremioBox/discussions) |
| Understand playback and boot changes | [Architecture](docs/architecture.md) · [17 platform patches](platform/README.md) |
| Build or customize the project | [Build guide](docs/building.md) · [Home source](launcher/README.md) · [Brand assets](docs/branding.md) |
| Help with the next release | [Roadmap](docs/roadmap.md) · [Contributing](CONTRIBUTING.md) |

The repository contains platform patches, a pinned source manifest, the product overlay, Home source and image tools. Each release after the first was produced by a declared, verified change to the previous image ([r7 changes](releases/r7-changes.json)). A clean full Android build from this public repository is still pending; the [build guide](docs/building.md) distinguishes the tested repack from the full build procedure.

## Credits and licensing

Built on [LineageOS](https://lineageos.org/), [los-tv-x86](https://github.com/los-tv-x86/lineage_bass_android), [Android-x86](https://www.android-x86.org/), [Mesa](https://www.mesa3d.org/), [drm_hwcomposer](https://gitlab.freedesktop.org/drm-hwcomposer/drm-hwcomposer), Intel's media stack and the Android Generic / AAROPA ecosystem. Stremio and mpv retain their original licenses.

Original tools, documentation, artwork and Home launcher use MIT. Platform changes retain their upstream licenses. [License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md).

StremioBox is an independent community project, unaffiliated with Stremio or LineageOS.
