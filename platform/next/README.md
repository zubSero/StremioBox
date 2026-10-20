# Next-release candidate: standby recovery and app stores

[Project](../../README.md) · [Build guide](../../docs/building.md#next-release-candidate) · [Standby findings](../../docs/standby-and-apps.md)

This directory contains source changes dated 2026-10-13. Their result ships in the **r7** image as a verified repack (see [r7 changes](../../releases/r7-changes.json)); a full source build with these patches is still pending. Published r5/r6 inputs and downloads keep their original bytes.

`inputs.json` pins the base lock, new patches, signed app-store APKs and corresponding source archives. `tools/prepare_platform.py --next-release --store-apks ...` inserts 0018 immediately after 0001, applies 0019 to the staged product, and copies the verified APKs. The default preparation path still uses the published 17 ports.

| Change | Purpose |
| --- | --- |
| 0018, frameworks/native | Restore VT_AUTO before VT_ACTIVATE in ConsoleManagerThread destruction; replace VT_WAITACTIVE with at most 20 polls separated by 10 ms |
| 0019, product/stremiobox | Seed Flicky and Aurora Store once alongside Stremio; preserve installed apps, user updates and later removals |
| 0020, hardware/libaudio | 5.1 primary output encoded as an AC-3 bitstream on HDMI, for TVs that only accept stereo LPCM but pass Dolby to an optical soundbar. See [audio-ac3](audio-ac3/README.md) |
| 0021, product/stremio | Convert Stremio's millisecond audio/subtitle delay to mpv seconds; a 100 ms tweak no longer freezes the picture |

0020 and 0021 (dated 2026-10-20) ship in the **r8** image as a verified repack (see [r8 changes](../../releases/r8-changes.json)); they are not yet part of `inputs.json` or a full source build. [audio-ac3](audio-ac3/README.md) has the reproducible HAL build, the boot overlay used on the development NUC and the verification record.

Home 1.1 already lists installed TV and regular launcher apps under **Apps & settings**. Stremio remains the main action. No launcher binary change is needed.

The physical NUC uses an exact-build native hotfix equivalent to 0018, plus guarded boot overlays. The native source patch has not been compiled into a fresh public image. Short standby, HDMI reconnect, reboot and store UI checks passed; overnight standby and a full source-build/fresh-data installation remain pending. See `device-hotfix-verification.json` for sanitized verification metadata.

Store APKs remain external build inputs. Download the exact URLs in `inputs.json`, preserve signatures, verify bytes and SHA-256, and save them as `Flicky.apk` and `AuroraStore.apk`. Keep each pinned source archive and its GPL notices available with any binary redistribution. The development source bundle includes those archives; Git contains their references and hashes.
