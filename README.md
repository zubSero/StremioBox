<div align="center">

![StremioBox](docs/assets/boot-screen.png)

# StremioBox

**Android 16 for an Intel NUC running Stremio on your TV.**

[![Intel NUC preview](https://img.shields.io/badge/download-Intel%20NUC%20preview-8b7bff?style=flat-square)](https://github.com/zubSero/StremioBox/releases/tag/r8)
[![Android 16](https://img.shields.io/badge/Android-16-65dfc1?style=flat-square&logo=android&logoColor=white)](docs/architecture.md)
[![Repository checks](https://github.com/zubSero/StremioBox/actions/workflows/validate.yml/badge.svg)](https://github.com/zubSero/StremioBox/actions/workflows/validate.yml)

[**Download**](https://github.com/zubSero/StremioBox/releases/tag/r8) · [**Installation**](docs/installation.md) · [**Changelog**](CHANGELOG.md) · [**Website**](https://zubsero.github.io/StremioBox/) · [**Nederlands**](README.nl.md)

</div>

StremioBox is a bootable Android TV system image based on Android 16 / LineageOS 23.2. It includes a remote-operated Home screen, Stremio TV 1.10.4 and fixes for Intel video output, HDMI audio, Bluetooth reconnection and subtitles. Playback uses Stremio's existing mpv interface, including its seek bar and player controls.

**This preview has been tested on one configuration: Intel NUC10i5FNH, Intel UHD graphics, Intel AX201 Bluetooth, a Homatics B21 remote and an LG HDR TV.** Other PCs and remotes need their own testing. The disk installer and long-duration playback tests are still pending; start with a live USB boot.

![StremioBox Home on the physical Intel NUC, with Aurora Store and Flicky under Apps & settings](docs/assets/home-r7-app-stores.png)

## What works on the tested NUC

| Feature | Observed result | Current limit |
| --- | --- | --- |
| 4K HDR10 video | HEVC Main10 uses Intel hardware decoding; the TV enters HDR mode with correct picture and audible sound | Tested around 24 fps in short samples; 4K60 and other HDR formats are unverified |
| Stremio controls | The existing mpv interface and seek bar remain available | VLC and ExoPlayer have not been validated |
| HDMI audio | Sound works before and after display standby; 5.1 is sent as Dolby Digital, decoded as real 5.1 by an optical soundbar behind the TV | Receivers that take multichannel PCM over HDMI also get AC-3; stereo sources stay on the front speakers |
| Bluetooth remote | Ordinary Homatics keys work after reboot without repeating the pairing combination | The physical power-button cycle needs a separate retest |
| Display standby | Film picture, sound and remote control recover after Android sleep/wake commands | Long-standby hang fixed in r7; overnight physical retest pending; true S3 suspend unverified |
| Subtitles | External SRT subtitles follow Disabled, language selection and audio-track changes | Eight development regression cases; not every subtitle format |
| Home screen | English labels, D-pad navigation, Stremio, settings and installed apps | Home 1.1 was also checked after a physical reboot |
| App stores | Aurora Store and Flicky open from Home and survive reboot | Complete app installation through each store still to be tested; no Google Play services |

[Hardware details](docs/hardware.md) · [Test methods and results](docs/testing.md)

## New in this release — 5.1 Surround Sound

- **Real 5.1 through the TV, clear dialogue.** Audio now leaves the NUC as Dolby Digital 5.1. A soundbar or surround system on the TV's optical output decodes it with dialogue on the centre speaker, instead of receiving a stereo mix in which voices drowned. Set the TV's digital audio output to Auto or Passthrough. [How it works](platform/next/audio-ac3/README.md)
- **The sync option works.** Adjusting audio or subtitle sync in the Stremio player no longer freezes the picture.
- **Sound comes back by itself** after the TV switched to another input or app and back.
- **Optional NuvioTV:** prefer [NuvioTV](docs/nuvio.md)? Install it yourself and StremioBox gives it HDR10 output; one command applies working settings and copies your Stremio addons. Stremio remains the default.

Earlier releases added the standby fix, Aurora Store and Flicky, quiet standby and an optional [rescue system](docs/rescue.md); all remain included. The physical NUC runs the changed audio files from its development installation, but was not reflashed with the new ISO. [Test boundary](docs/testing.md#surround-sound-release)

## Download and try it

The current download is **Intel NUC Preview — 5.1 Surround Sound**. It includes all earlier fixes, English Home 1.1, the standby fix, both app stores and 5.1 output. [Read the changes](CHANGELOG.md#surround-sound).

1. Download the [native download ZIP](https://github.com/zubSero/StremioBox/releases/download/r8/StremioBox-r8-native-download.zip) and extract it.
2. **Windows:** double-click `Download-StremioBox.cmd`. **Linux/macOS:** open a terminal in the extracted folder and run `bash tools/download.sh --output downloads`. No Python is required.
3. Follow the [USB boot and installation guide](docs/installation.md). Allow about **6 GB free** for the download and assembled image.
4. After Android starts, pair your remote and sign in to Stremio with your own account. No accounts or add-ons are configured in the image.

The helper joins two download parts into one ISO and verifies their SHA-256 hashes. The resulting ISO is about **2.89 GB**. For manual downloads, source archives, the rescue kit and checksums, open the [release page](https://github.com/zubSero/StremioBox/releases/tag/r8).

**Already running r5, r6 or r7?** The 5.1 output and the sync fix replace system files and need a reinstall with r8; on r5/r6 the stores can also be added over ADB. [Update options](docs/installation.md#update-an-existing-installation).

**Already using the initial image with Dutch Home?** Install the [English Home update](docs/installation.md#update-an-existing-installation) to change the launcher language. It uses the same signing certificate and survives reboot.

[ADB update instructions without Python](docs/adb-installation.md) are available for existing installations. Full-system ADB migration requires supported root access and a compatible boot/disk layout; a portable system installer is still pending.

**No USB stick?** Read the [USB-free installation options](docs/without-usb.md), which distinguish the tested app update from system migration and network-boot work still needed.

<details>
<summary>Image filename and checksum</summary>

The release's technical identifier is `r8`; filenames and download URLs use it.

```text
StremioBox-Android16-r8-nuc10_tv.iso
2,886,467,584 bytes
SHA-256: 2996c6c07b832526bdaca3012047da648fc85b50477cd7b9e750d039717674ec
```

[Download manifest](releases/r8.json) · [Image verification](releases/r8-image-verification.json) · [Image delta](releases/r8-image-delta.json)

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
| Use NuvioTV instead of or next to Stremio | [NuvioTV guide](docs/nuvio.md) |
| Repair a box that no longer starts | [Rescue system](docs/rescue.md) |
| Report a bug or another hardware configuration | [Issues](https://github.com/zubSero/StremioBox/issues/new/choose) |
| Ask a setup question | [Discussions](https://github.com/zubSero/StremioBox/discussions) |
| Understand playback and boot changes | [Architecture](docs/architecture.md) · [17 platform patches](platform/README.md) |
| Build or customize the project | [Build guide](docs/building.md) · [Home source](launcher/README.md) · [Brand assets](docs/branding.md) |
| Help with the next release | [Roadmap](docs/roadmap.md) · [Contributing](CONTRIBUTING.md) |

The repository contains platform patches, a pinned source manifest, the product overlay, Home source and image tools. Each release after the first was produced by a declared, verified change to the previous image ([r8 changes](releases/r8-changes.json)). A clean full Android build from this public repository is still pending; the [build guide](docs/building.md) distinguishes the tested repack from the full build procedure.

## Credits and licensing

Built on [LineageOS](https://lineageos.org/), [los-tv-x86](https://github.com/los-tv-x86/lineage_bass_android), [Android-x86](https://www.android-x86.org/), [Mesa](https://www.mesa3d.org/), [drm_hwcomposer](https://gitlab.freedesktop.org/drm-hwcomposer/drm-hwcomposer), Intel's media stack and the Android Generic / AAROPA ecosystem. Stremio and mpv retain their original licenses.

Original tools, documentation, artwork and Home launcher use MIT. Platform changes retain their upstream licenses. [License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md).

StremioBox is an independent community project, unaffiliated with Stremio or LineageOS.
