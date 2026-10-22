<div align="center">

![StremioBox](docs/assets/boot-screen.png)

# StremioBox

### Turn a small Intel PC into a Stremio box for your TV.

**4K HDR · Dolby Digital 5.1 · one remote · no Google account**

[![Download](https://img.shields.io/github/v/release/zubSero/StremioBox?label=download&style=for-the-badge&color=8b7bff)](https://github.com/zubSero/StremioBox/releases/latest)
[![Website](https://img.shields.io/badge/website-visit-65dfc1?style=for-the-badge)](https://zubsero.github.io/StremioBox/)

[**Get started**](#-get-started) · [**What you get**](#-what-you-get) · [**Questions**](#-questions) · [**Nederlands**](README.nl.md)

</div>

---

StremioBox is a free system you put on an **Intel NUC** (a palm-sized PC). Plug it into your TV, pick up the remote, and it starts straight into a simple home screen with **Stremio** — no desktop, no setup wizard full of accounts, no ads.

![The StremioBox home screen on a TV](docs/assets/home-r7-app-stores.png)

## ✨ What you get

| | |
| --- | --- |
| 🎬 **Films in 4K HDR** | Smooth 4K with real HDR on your TV, using the PC's own video chip. |
| 🔊 **Proper surround sound** | Dolby Digital 5.1 to your soundbar or receiver, so dialogue stays clear. Stereo TVs work too. |
| 🎮 **One remote** | Pair a Bluetooth TV remote once; it keeps working after restarts and standby. |
| 💬 **Subtitles that behave** | Turn them off, switch language or audio track — they follow along. |
| 🌙 **Wakes up reliably** | Standby and wake work like a normal TV box, picture and sound come back. |
| 🛒 **More apps if you want** | Aurora Store and Flicky are built in for installing other apps. |
| 🧩 **NuvioTV, if you prefer it** | Optional: install NuvioTV and StremioBox gives it HDR and copies your Stremio addons. [How](docs/nuvio.md) |
| 🛟 **A safety net** | An optional rescue system lets you repair the box if Android ever stops starting. [How](docs/rescue.md) |

## 🤔 Is this for me?

StremioBox is a good fit if:

- ✅ you have (or want to buy) an **Intel NUC** — it was tested on the **NUC10i5FNH**
- ✅ you already use **Stremio** or want a dedicated box for it
- ✅ you don't mind installing from a **USB stick** once

Good to know before you start:

- It has been tested on **one** setup so far (Intel NUC10i5FNH, LG TV, Homatics B21 remote). Other PCs may work, but nobody has checked yet — [tell us](https://github.com/zubSero/StremioBox/issues/new/choose) if you try one!
- It's a community project, not a commercial product. Try it from USB first; installing to the disk is possible but not fully tested yet.
- Streaming services that need certified Android devices (Netflix and friends) are not the goal here.

## 🚀 Get started

1. **Download** the [download helper](https://github.com/zubSero/StremioBox/releases/download/r9/StremioBox-r9-native-download.zip) and unzip it.
2. **Run it.** On Windows, double-click `Download-StremioBox.cmd`. On Mac or Linux, run `bash tools/download.sh --output downloads` in that folder. It fetches the image (about 2.9 GB) and checks it is complete and untouched. Keep about 6 GB free.
3. **Put it on a USB stick** with a tool like [balenaEtcher](https://etcher.balena.io/) or Rufus, plug it into the NUC and start from USB. → [Step-by-step installation guide](docs/installation.md)
4. **Pair your remote, sign in to Stremio** with your own account, and start watching. 🍿

> **Tip for surround sound:** set your TV's digital audio output to **Auto** or **Passthrough** so your soundbar receives Dolby Digital.

## 🆕 What's new

**Surround Sound & NuvioTV** — the first release we recommend for everyone:

- 🔊 Real **5.1 Dolby Digital** through your TV to the soundbar — no more drowned-out dialogue.
- 🔁 **Sound comes back by itself** if the TV switched inputs and lost the audio.
- ⏱️ The **audio/subtitle sync** setting in Stremio works without freezing the picture.
- 🧩 Optional **NuvioTV** support with HDR.

[See everything that changed →](CHANGELOG.md)

## ❓ Questions

<details>
<summary><b>Do I need to know anything about Linux or Android?</b></summary>

No. Download, write to USB, start from USB, use the remote. The only optional extras (NuvioTV setup, updating an older install) use a computer command, and the guides show you exactly what to type.
</details>

<details>
<summary><b>Which remote works?</b></summary>

It was tested with the Homatics B21 Bluetooth remote. Most Bluetooth TV remotes and USB keyboards should work; a keyboard is handy for the first setup.
</details>

<details>
<summary><b>I already run an older StremioBox. Do I need to reinstall?</b></summary>

For the new sound and NuvioTV features, yes — they are part of the system. Some smaller things can be updated without reinstalling. [Update options](docs/installation.md#update-an-existing-installation)
</details>

<details>
<summary><b>No sound, or my soundbar only shows stereo?</b></summary>

Set the TV's digital audio output to Auto/Passthrough and make sure you run the latest release. More fixes in the [troubleshooting guide](docs/troubleshooting.md).
</details>

<details>
<summary><b>I don't have a USB stick.</b></summary>

There are a few other routes, each with its own limits. [Installing without USB](docs/without-usb.md)
</details>

<details>
<summary><b>Is it safe?</b></summary>

The image contains no accounts, keys or personal data — you set everything up yourself. It's a developer-style build, so keep it on your home network. [Security details](SECURITY.md)
</details>

## 🤝 Help and community

- 🐛 Something not working? [Report a problem](https://github.com/zubSero/StremioBox/issues/new/choose)
- 💬 Want to ask something? [Discussions](https://github.com/zubSero/StremioBox/discussions)
- 🛠️ Want to help? Pull requests are welcome — fixes, other hardware, translations, docs. [How to contribute](CONTRIBUTING.md)

---

<details>
<summary><b>🔧 For the technically curious</b></summary>

StremioBox is a bootable Android TV image based on **Android 16 / LineageOS 23.2** with Stremio TV 1.10.4, a remote-first Home launcher and fixes for Intel HDR video (HEVC Main10, HDR10), HDMI audio (AC-3 bitstream encoding in the audio HAL), Bluetooth reconnection, display standby and subtitles. Playback uses Stremio's own mpv interface.

| Where | What |
| --- | --- |
| [Hardware & compatibility](docs/hardware.md) | What was tested and what is unverified (Dolby Vision, HLG, AV1, 4K60, HDMI-CEC…) |
| [Test results](docs/testing.md) | How each release was checked, and the limits of those checks |
| [Architecture](docs/architecture.md) | How playback, audio, HDR and boot changes fit together |
| [Platform patches](platform/README.md) · [next patches](platform/next/README.md) | The source changes |
| [Build guide](docs/building.md) | Reproducing the image; full source build status |
| [Changelog](CHANGELOG.md) | Every release in detail |
| [Home launcher source](launcher/README.md) · [Brand assets](docs/branding.md) | Launcher and artwork |

**Current image:** `StremioBox-Android16-r9-nuc10_tv.iso`, 2,886,336,512 bytes, SHA-256 `06267691ec264d0233d6c34c4d32740fc9df393bcb55bd3b717ee103fa0eef1e` · [manifest](releases/r9.json) · [verification](releases/r9-image-verification.json) · [delta](releases/r9-image-delta.json). Each release after the first is a declared, verified change to the previous image; a clean full Android build from this repository is still pending.

</details>

## 📜 Credits and license

Built on [LineageOS](https://lineageos.org/), [los-tv-x86](https://github.com/los-tv-x86/lineage_bass_android), [Android-x86](https://www.android-x86.org/), [Mesa](https://www.mesa3d.org/), [drm_hwcomposer](https://gitlab.freedesktop.org/drm-hwcomposer/drm-hwcomposer), Intel's media stack and the Android Generic / AAROPA community. Stremio, mpv and NuvioTV keep their own licenses.

Our own tools, docs, artwork and Home launcher are MIT-licensed; platform changes keep their upstream licenses. [License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)

StremioBox is an independent community project and is not affiliated with Stremio, LineageOS, Nuvio or Dolby.
