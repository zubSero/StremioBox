# r5 platform and r6 Home validation

[Back to the project](../README.md) · [Download identity](../releases/r5.json)

The original r5 ISO has SHA-256 `37a6aa352809ba4960842b90dfd83ad89fc82dc1c82fe24828cdf2f63c576265`. Results below describe the final r5 system on the [test configuration](hardware.md), unless a narrower scope is stated. Private device logs and accounts are not published.

## Physical NUC

| Check | Observation |
| --- | --- |
| Ordinary reboot | The installed system returned to StremioBox Home; packaged native and branding payload hashes checked |
| Remote after reboot | User confirmed ordinary Homatics arrow keys work without pairing combination |
| 4K HEVC Main10 HDR10 | MediaCodec / Intel VAAPI hardware path, P010 GPU buffers, BT.2020/PQ and active HDMI HDR metadata; user confirmed LG HDR mode and good picture/sound |
| Playback sample | 179.679 s, 12 displayed-frame drops and 0 decoder drops |
| Post-standby sample | 173.506 s, 6 displayed-frame drops and 0 decoder drops; counters reset during recovery, so samples are not additive |
| H.264 SDR | 640×360 sample for 4.458 s, 0 drops; limited codec smoke test |
| HDMI audio | Active AudioTrack and advancing ALSA frames, plus audible output confirmed by the user before/after standby |
| Display standby | Synthetic Android sleep/wake while film was foreground; player, SurfaceFlinger and Bluetooth stayed alive; picture and sound recovered |
| Subtitles | External SRT language selection and audio-track switches; Disabled returned `sid=no` with no overlay; eight Java regression cases passed during development |
| Vulkan | Seven Skia Vulkan UI frames with Intel's driver loaded; temporary test renderer setting restored afterwards |
| Tested app reinstall | Original signed 1.10.4 reinstall retained user data and compatible player integration |
| Incompatible update | Mutated private-field fixture rejected by the update guard |

The source contained an AC3 5.1 audio track, but this does **not** certify bitstream passthrough or receiver codec support. The audio claim is audible primary HDMI output.

## Image and first boot

- Verified full-filesystem delta against compiled r4. Unlisted file contents, ownership, modes, xattrs and symlinks remained unchanged.
- Verified packaged kernel, initrd, recovery image and system hashes; the [public verification record](../releases/r5-image-verification.json) lists them.
- Checked the hybrid BIOS/UEFI boot structures and matching root volume label.
- Booted the final ISO in a diskless UEFI VM with fresh Android data. Setup, Home and first-boot original signed app seeding reached Stremio's sign-in screen.
- No personal accounts, developer ADB keys or Bluetooth bonds included in the release image.

Fresh-data VM testing does not certify all Intel playback features or the destructive disk installer. The film/HDR/audio checks came from the physical NUC.

## Still pending

Physical Homatics power-button cycle on final r5, multi-hour playback/thermal soak, destructive installer validation on a spare disk, other hardware, 4K60 and the formats listed as unverified in the [hardware matrix](hardware.md).

## Repository CI

GitHub Actions validates source/asset locks, release metadata, local documentation links and helper syntax. Download tests cover reconstruction, corrupt parts, an invalid final image, interrupted transfers and preservation of existing output. Source-preparation tests cover pinned revisions, conflicts and rollback. CI does not compile Android or replace physical hardware testing.

The real 2,873,884,672-byte release image was also reconstructed offline with the public download helper and matched its original SHA-256. The website was rendered in an isolated browser at desktop, 390 px and 320 px viewport widths; image loading, layout bounds, download-command tabs, copy feedback and expandable questions were checked.

## r6 English Home checks

The r6 ISO has SHA-256 `f5e8642165e732c0a44dac4a87a36e56b297ed3e1c928f39d2f4dec8e1783550`. Only the Home APK changes against r5: 19,581 other system entries retain their contents, modes, ownership, xattrs and symlinks. Kernel, initrd and recovery hashes are unchanged. See [the delta](../releases/r6-home-delta.json) and [image record](../releases/r6-image-verification.json).

The signed English Home 1.1 update was installed on the physical r5 NUC. Package version 2/1.1 and all visible English labels were checked, and the update/English UI survived an ordinary reboot. The current screenshot is an actual capture of this Home interface. This does not claim that the physical NUC was reflashed with r6 or that the full playback matrix was rerun for a text-only launcher change.
