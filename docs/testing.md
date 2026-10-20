# Test results and known limits

[Back to the project](../README.md) · [Changelog](../CHANGELOG.md) · [Current image identity](../releases/r6.json)

The physical playback tests below describe **Intel NUC Preview — Initial Release** (technical tag `r5`) on the [test configuration](hardware.md). **English Home** (`r6`) changes the launcher and preserves the native platform; its separate checks appear below. Private device logs and accounts are not published.

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

Physical Homatics power-button cycles on the public platform, multi-hour playback/thermal soak, destructive installer validation on a spare disk, other hardware, 4K60 and the formats listed as unverified in the [hardware matrix](hardware.md).

## Repository CI

GitHub Actions validates source/asset locks, release metadata, local documentation links and helper syntax. Download tests cover reconstruction, corrupt parts, an invalid final image, interrupted transfers and preservation of existing output. Source-preparation tests cover pinned revisions, conflicts and rollback. CI does not compile Android or replace physical hardware testing.

The Python-free helpers also have corruption, wrong-final-hash, offline, manifest-validation and existing-output tests. CI runs the actual Windows PowerShell 5.1 helper on Windows and the shell helper on Linux; Python runs the contributor test harness, but is not used by these download helpers. On 2026-10-06, native Windows PowerShell downloaded both English Home release pieces from GitHub and assembled the 2,874,343,424-byte ISO. The Linux shell helper assembled those pieces offline under Ubuntu/WSL, and 7-Zip 26.03 combined them with `-tsplit`. All three produced SHA-256 `f5e8642165e732c0a44dac4a87a36e56b297ed3e1c928f39d2f4dec8e1783550`. The shell helper's macOS branch uses system tools but has not yet been executed on a Mac.

The real 2,873,884,672-byte release image was also reconstructed offline with the public download helper and matched its original SHA-256. The website was rendered in an isolated browser at desktop, 390 px and 320 px viewport widths; image loading, layout bounds, download-command tabs, copy feedback and expandable questions were checked.

<a id="english-home-update"></a>

## English Home update

The r6 ISO has SHA-256 `f5e8642165e732c0a44dac4a87a36e56b297ed3e1c928f39d2f4dec8e1783550`. Only the Home APK changes against r5: 19,581 other system entries retain their contents, modes, ownership, xattrs and symlinks. Kernel, initrd and recovery hashes are unchanged. See [the delta](../releases/r6-home-delta.json) and [image record](../releases/r6-image-verification.json).

The signed English Home 1.1 update was installed on the physical r5 NUC. Package version 2/1.1 and all visible English labels were checked, and the update/English UI survived an ordinary reboot. The current screenshot is an actual capture of this Home interface. This does not claim that the physical NUC was reflashed with r6 or that the full playback matrix was rerun for a text-only launcher change.

The final r6 ISO also passed a diskless UEFI live boot in QEMU/KVM with fresh Android data. Boot completed, package scanning selected Home 1.1, and first boot seeded the original signed Stremio TV 1.10.4 x86_64 APK with the expected hash. English Home resumed and its visible labels were checked in a captured guest screenshot. Only ephemeral guest settings were provisioned to reach Home; this does not certify the complete setup wizard or disk installer. The virtual graphics swaps red and blue image channels, so artwork colors and the public screenshot were verified on the physical NUC. See [the startup validation record](../releases/r6-boot-validation.json).

## Standby and app-store candidate — 2026-10-13

*Superseded by the [r7 results](#standby-and-app-stores-release) for the public image; kept as the development-device record.*

The [candidate report](standby-and-apps.md) records the later long-standby failure and device hotfix checks separately from r5/r6 acceptance. Two full boots, three short sleep/wake cycles, two DRM connector reconnect cycles and four completed console-manager destructor calls passed without new ANRs. These are short development-device tests, not a completed overnight physical test or a new ISO boot test.

Aurora Store and Flicky APK hashes, x86_64 support and TV launch activities were checked against official F-Droid inputs. Both appeared in Home and survived reboot. Flicky fetched its catalogue; Aurora reached first-use onboarding. Rerunning seeding preserved package install/update timestamps. No store account or terms were accepted and end-to-end user app installation is pending.

<a id="surround-sound-release"></a>

## 5.1 Surround Sound release (r8) — 2026-10-21

The r8 ISO has SHA-256 `04525a485994c576cb53bc72a654aec569545ead16fa5375d62c0313b1422932`. It was derived from the verified r7 ISO with [`repack_image.py`](../tools/repack_image.py) and a [declared change list](../releases/r8-changes.json). Exactly three system entries were replaced: the 32-bit primary audio HAL, the audio policy and the Stremio bridge library. 19,581 other entries keep their contents, modes, ownership, SELinux labels and symlinks; kernel, initrd, recovery and boot structures are unchanged. See [the delta](../releases/r8-image-delta.json) and [image record](../releases/r8-image-verification.json).

The HAL comes from [`build.sh`](../platform/next/audio-ac3/build.sh) with pinned sources and patch 0020; two clean builds in different directories produced identical bytes.

A diskless fresh-data UEFI live boot in QEMU/KVM repeated every r7 check (app and store seed, compositor hash, no fingerprint feature, Home, three sleep/wake cycles without ANRs) and added an audio check: with an emulated Intel HDA device, a 6-channel AAudio stream ran through a 6-channel mixer, the HAL reported its AC-3 encoder and bitstream output, and both audio services kept running without tombstones. [Boot record](../releases/r8-boot-validation.json).

On the development NUC the same three files ran through a guarded boot overlay for two full reboots, connected to an LG TV with a Logitech 5.1 system on the TV's optical output:

- A direct AC-3 channel-identification burst played on all six speakers, including centre.
- Stremio's mpv decoded an E-AC-3 film to 5.1; the HAL sent AC-3 with the IEC958 non-audio bit set. The receiver showed Dolby Digital, dialogue came from the centre speaker and lip sync was correct at 0 ms.
- Stremio's audio delay steps of 100 ms changed sync without freezing the picture.

**Test boundary:** the physical NUC was not reflashed with the r8 ISO. Receivers that accept multichannel PCM over HDMI, other TVs and long playback sessions were not tested.

<a id="standby-and-app-stores-release"></a>

## Standby & App Stores release (r7) — 2026-10-14

The r7 ISO has SHA-256 `65b07feafd70670954231afc6a69a6b850445d67197c4d53f3c1cf1aff010bb8`. It was derived from the verified r6 ISO with [`repack_image.py`](../tools/repack_image.py) and a [declared change list](../releases/r7-changes.json). Exactly five system entries changed (three replaced, two added); 19,579 other entries keep their contents, modes, ownership, SELinux labels and symlinks. Kernel, initrd, recovery and the UEFI/BIOS/GPT boot structures are unchanged. See [the delta](../releases/r7-image-delta.json) and [image record](../releases/r7-image-verification.json).

A diskless fresh-data UEFI live boot in QEMU/KVM completed. The guest reported the fixed SurfaceFlinger hash, no fingerprint feature, Stremio, Flicky and Aurora Store installed with their expected hashes, install permission for both stores and both first-boot markers. Home resumed with the stores in **Apps & settings**. Three virtual sleep/wake cycles kept the same SurfaceFlinger process, produced no ANR files and no IVirtualHal errors. [Boot record](../releases/r7-boot-validation.json).

The rescue kit was tested in QEMU/KVM: direct boot with SSH, activation from a live r7 guest, boot through the added GRUB entry and removal. [Rescue record](../releases/r7-rescue-validation.json).

**Test boundary:** the physical NUC runs the same SurfaceFlinger, first-boot script, store APKs and fingerprint file through its development installation (two reboots, short standby and HDMI reconnect cycles passed). It was not reflashed with the r7 ISO. The overnight standby test with the physical power button, a full disk installation and complete in-store app installation are still pending. The Home screenshot with both stores is a capture from the physical NUC.
