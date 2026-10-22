# NuvioTV on StremioBox (optional)

[Back to the project](../README.md) · [Troubleshooting](troubleshooting.md) · [ADB guide](adb-installation.md)

StremioBox ships with **Stremio** as its player. [NuvioTV](https://github.com/NuvioMedia/NuvioTV) is a separate, open-source (GPL-3.0) Android TV app that uses the same Stremio addons and adds profiles, built-in TorBox/Premiumize support and phone-based addon management. It is still a beta.

Nuvio is **opt-in**: nothing changes unless you install it yourself. From r8 on, the image contains the pieces that make Nuvio work well on the NUC:

| Without Nuvio | With Nuvio installed |
| --- | --- |
| Nothing runs; Stremio stays the default | The HDR adapter couples automatically to a reviewed Nuvio version: HDR10 output on the TV, like Stremio |
| | 5.1 Dolby Digital output and the HDMI audio watchdog work for Nuvio too (they are system features) |
| | `stremiobox-nuvio-setup` applies the recommended player settings and copies your Stremio addons |

## 1. Install NuvioTV

Use the official release: [NuvioMedia/NuvioTV releases](https://github.com/NuvioMedia/NuvioTV/releases), file `app-full-x86_64-release.apk`. Check its SHA-256 against the value GitHub shows next to the asset, then install it over ADB ([ADB setup](adb-installation.md)):

```sh
adb install app-full-x86_64-release.apk
```

The HDR adapter was reviewed for **1.1.0-beta.7**. Other versions install and play normally but keep SDR output until their native player library has been reviewed (see [limits](#limits)).

## 2. Sign in or continue without an account

Open Nuvio from Home → Apps & settings. On its welcome screen either scan the QR code to sign in to a Nuvio account (addons and settings then sync to your other Nuvio devices) or choose **Continue without account**. Nuvio ignores addon installs while this welcome screen is shown.

## 3. Apply the recommended settings and copy your addons

```sh
adb shell stremiobox-nuvio-setup all
```

- `settings` sets Nuvio's player to **libmpv** with **direct hardware decoding**, turns on **frame rate matching** (24 Hz for films) and turns off the automatic switch to ExoPlayer. Nuvio is restarted.
- `addons` reads the addons installed in Stremio on this box and installs them in Nuvio through its own install links. Configured addons keep their settings and debrid keys. URLs never leave the box; only host names are printed. Addons whose server no longer answers are reported as skipped.
- `all` does both.

Why these settings: Nuvio's default ExoPlayer engine cannot display 4K 10-bit HDR video on this Intel GPU (it stays at *Starting stream…*), and without frame rate matching 23.976 fps films show a small hitch every ~40 seconds at 60 Hz.

## 4. TorBox, Real-Debrid and other services

Addons such as Torrentio or Comet that you configured with a debrid key keep using it. To connect TorBox directly (cloud library, cache checks), open Nuvio **Settings → Integrations → Connected Services → Torbox** and approve the code at `tor.box/link` on your phone.

## Limits

- **New Nuvio versions:** the adapter wraps Nuvio's native player library. A Nuvio update that changes it is detected by checksum and left alone: playback works, but in SDR, and `logcat -s nuvio-hdr` shows `not reviewed`. Updates to the reviewed list arrive with StremioBox releases.
- **HDR detection:** the NUC's hardware decoder reports BT.2020 colours without the transfer function, so the adapter treats BT.2020 video as HDR10. HLG is detected when mpv reports it. Dolby Vision streams play their HDR10 base layer.
- **Switching on HDR** recreates mpv's video output once at the start of a video (a brief black frame).
- ExoPlayer in Nuvio remains unusable for 4K 10-bit video on this hardware.

## Turn it off

- HDR adapter only: `adb shell touch /data/local/nuvio-hdr-disabled`, then restart the box.
- Nuvio itself: uninstall it like any app. Stremio and its settings are never touched.

Nuvio, Stremio, TorBox and Dolby are trademarks of their owners; StremioBox is independent of all of them.
