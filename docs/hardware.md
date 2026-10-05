# Hardware and compatibility

[Back to the project](../README.md) · [Test report](testing.md)

**The release target is one tested Intel NUC configuration.** Similar hardware may work, but that is not a support claim.

| Component | Tested configuration |
| --- | --- |
| Computer | Intel NUC10i5FNH |
| GPU | Intel UHD, Comet Lake GT2 (`8086:9b41`) |
| Bluetooth | Intel AX201 (`8087:0026`) |
| Remote | Homatics B21, Bluetooth LE HID |
| Display | LG HDR-capable TV over HDMI; exact model not recorded publicly |
| OS | Android 16 / SDK 36, LineageOS 23.2, x86_64 |
| Kernel | `6.18.21-zenith+` |
| App | Original signed Stremio TV 1.10.4, x86_64 |

## Playback scope

| Capability | Status |
| --- | --- |
| 4K HEVC Main10 HDR10 at ~24 fps | Physically verified, hardware decoded |
| 10-bit P010, BT.2020 / PQ, HDMI HDR metadata | Verified on the tested Intel path |
| H.264 SDR | Short low-resolution playback check; not a 4K profile certification |
| HDMI sound | Primary HDMI output audible, including after display standby |
| Subtitle disabled/language changes | External SRT cases verified in Stremio mpv |
| Homatics ordinary keys after reboot | Physically verified |
| Display standby / wake with film playing | Verified using synthetic Android sleep/wake plus physical picture/sound confirmation |
| Physical Homatics power-button cycle on final r5 | Separate retest pending |
| Intel Vulkan driver | UI rendering smoke test passed; not conformance testing |

## Not verified yet

Other NUC generations, AMD/NVIDIA GPUs, AV1, every H.264/HEVC profile, 4K60 video, Dolby Vision, HLG, VLC, ExoPlayer, audio bitstream passthrough, HDMI-CEC and true ACPI S3 suspend. Widevine levels and subscription-service DRM certification are not claimed.

Display standby intentionally leaves Android running to preserve Bluetooth and playback recovery. A TV may show “No signal” while HDMI output is off. That does not by itself indicate a failed wake; the important check is that picture, sound and remote return afterwards.

A multi-hour thermal/playback soak is still pending. Short tests are useful evidence, not a reliability guarantee. [Report another configuration](https://github.com/zubSero/StremioBox/issues/new?template=hardware.yml) with public model and PCI/USB IDs; leave out serial numbers, MAC addresses and account details.
