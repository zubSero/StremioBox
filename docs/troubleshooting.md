# Troubleshooting

[Back to the project](../README.md) · [Report a bug](https://github.com/zubSero/StremioBox/issues/new?template=bug.yml)

| Symptom | Useful first checks |
| --- | --- |
| No signal during standby | Expected while HDMI is off. Check that wake restores picture, sound and ordinary remote keys. Record whether Android stayed running. |
| Black playback | Confirm the app version, codec, HDR format and whether Home still renders. The validated path is Stremio mpv with HEVC Main10 HDR10 on the tested Intel GPU. |
| No audio | Confirm HDMI is the active output and check TV volume/input. Record app audio track and whether the same issue happens with an SDR sample. |
| Remote requires pairing again | Separate initial pairing from reconnect failure; state whether it followed reboot, display standby or deep suspend. Record remote and Bluetooth adapter model. |
| Subtitles despite Disabled | Record embedded versus external subtitles, selected audio track and app version. Do not post private stream URLs or subtitle-service tokens. |
| Vulkan “not supported” | Some feature-reporting apps test a different contract. r5 passed a specific Intel Skia UI smoke test, not every Vulkan conformance check. Name the reporting app and attach redacted output. |
| Download checksum failure | Rerun the helper; a corrupt part is rejected and a complete existing valid image is reused. Check free storage and use this release's matching manifest. |
| ADB unavailable | Use a trusted network, confirm the box address and authorize your own host key. First setup must have finished. Never publish your private ADB key. |

Include the revision, public hardware IDs, exact steps and expected/actual behavior in a report. Redact account identifiers, serials, MAC addresses, local/private network addresses, authentication links and access tokens from logs or screenshots.
