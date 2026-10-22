# Changelog

This history describes the downloadable images and their verified behavior. Dates use UTC. Release names describe the change; identifiers such as `r7` remain in filenames, tags and verification records so existing downloads stay traceable.

| Release | Published | What changed | Technical tag |
| --- | --- | --- | --- |
| [Intel NUC Preview — Surround Sound & NuvioTV](#surround-sound-and-nuviotv) | 2026-10-22 | First recommended release: everything from r8 plus stereo for screens without Dolby Digital and a safer audio watchdog | [`r9`](https://github.com/zubSero/StremioBox/releases/tag/r9) |
| [Intel NUC Preview — 5.1 Surround Sound](#surround-sound) (pre-release, superseded by r9) | 2026-10-22 | Real 5.1 (Dolby Digital) through TVs with an optical soundbar, sound back after TV input switches, working sync option, optional NuvioTV with HDR | [`r8`](https://github.com/zubSero/StremioBox/releases/tag/r8) |
| [Intel NUC Preview — Standby & App Stores](#standby-and-app-stores) | 2026-10-14 | Standby/HDMI hang fix, Aurora Store and Flicky, no console log spam, optional rescue kit | [`r7`](https://github.com/zubSero/StremioBox/releases/tag/r7) |
| [Intel NUC Preview — English Home](#english-home) | 2026-10-05 | English Home 1.1, an update APK for existing installations and a fresh installation image | [`r6`](https://github.com/zubSero/StremioBox/releases/tag/r6) |
| [Intel NUC Preview — Initial Release](#initial-release) | 2026-10-05 | First public image with StremioBox Home and the Intel playback, audio, Bluetooth and subtitle fixes | [`r5`](https://github.com/zubSero/StremioBox/releases/tag/r5) |

<a id="surround-sound-and-nuviotv"></a>

## Intel NUC Preview — Surround Sound & NuvioTV

**Published 2026-10-22 · Home 1.1 · Android 16 / LineageOS 23.2**

[Download](https://github.com/zubSero/StremioBox/releases/tag/r9) · [Installation](docs/installation.md) · [NuvioTV guide](docs/nuvio.md) · [Validation](docs/testing.md#surround-sound-and-nuviotv-release)

The first release marked as recommended. It contains everything from the [r8 pre-release](#surround-sound) — real Dolby Digital 5.1 through the TV, sound that comes back after TV input switches, the working Stremio sync option and optional NuvioTV with HDR — plus two fixes.

### Fixed: no sound on screens without Dolby Digital

- r8 always sent a Dolby Digital bitstream over HDMI. PC monitors with speakers, older TVs and other sinks that only accept PCM would have stayed silent or produced noise.
- r9 reads the screen's HDMI audio capabilities (ELD) each time playback starts. Only sinks that list AC-3 get the bitstream; all others get a stereo mix with the centre (dialogue) channel kept clear.

### Fixed: the audio watchdog could blink displays without HDMI audio

- A display that never reports HDMI audio (for example a DVI monitor) looked like a TV that had lost it, so the watchdog could cycle the screen during playback.
- The watchdog now only acts after the TV reported its audio capabilities at least once since boot.

### Image changes and verification

- Derived from the verified r8 image with [`repack_image.py`](tools/repack_image.py) and a [declared change list](releases/r9-changes.json): the audio HAL and the watchdog script; every other entry, kernel, initrd, recovery and boot structures unchanged. [Delta](releases/r9-image-delta.json).
- The HAL is again built reproducibly by [`build.sh`](platform/next/audio-ac3/build.sh) from the updated patch 0020; the watchdog comes from the updated patch 0022.
- The capability check was run on the development NUC (LG TV: AC-3 listed → bitstream) and against PCM-only and AC-3 ELD samples. Fresh-data UEFI boot in QEMU/KVM repeats all r8 checks. [Boot record](releases/r9-boot-validation.json).

<a id="surround-sound"></a>

## Intel NUC Preview — 5.1 Surround Sound

**Published 2026-10-22 · Home 1.1 · Android 16 / LineageOS 23.2**

[Download](https://github.com/zubSero/StremioBox/releases/tag/r8) · [Installation](docs/installation.md) · [How the 5.1 output works](platform/next/audio-ac3/README.md) · [Validation](docs/testing.md#surround-sound-release)

### Fixed: dialogue no longer drowns, real 5.1 through the TV

- Up to r7 the NUC sent only stereo PCM over HDMI. Many TVs report just stereo LPCM, so a soundbar or 5.1 system on the TV's optical output received stereo: the centre channel was folded into left and right, and dialogue got lost under music and effects. A Chromecast on the same TV sounded better because it sends Dolby Digital.
- r8 mixes Android audio in 5.1 and encodes it on HDMI as a Dolby Digital (AC-3, 640 kbit/s) bitstream, the format an optical link carries. The TV passes it on and the receiver decodes real 5.1 with dialogue on the centre speaker. This works for every app and every source format: E-AC-3, TrueHD, DTS, AAC 5.1 and stereo.
- Set the TV's digital audio output to **Auto** or **Passthrough**. Stereo material plays on the front speakers unless your receiver upmixes it.

### Fixed: the audio and subtitle sync option froze the picture

- Stremio passes its sync setting in milliseconds while the mpv player expects seconds, so a 100 ms tweak became 100 seconds: the picture froze while sound continued. r8 converts the unit; sync steps now work as intended.

### Fixed: no sound after switching the TV input

- After the TV switched to another input or one of its own apps and back, it sometimes stopped reporting its audio capabilities (ELD) to the NUC. The display kept working, but HDMI audio stayed silent until a restart.
- A small watchdog notices this during playback and briefly turns the display off and on (about 3 seconds black), after which sound returns. It only acts while something is playing, so it never pulls the TV back from another input.

### New: optional NuvioTV support (opt-in)

- Stremio stays the player. If you install [NuvioTV](docs/nuvio.md) yourself, r8 makes it work well on the NUC: an HDR adapter gives Nuvio's libmpv engine real HDR10 output like Stremio, and `adb shell stremiobox-nuvio-setup all` applies the settings that work on this hardware (libmpv, direct decoding, 24 Hz frame rate matching) and copies your Stremio addons, including their debrid configuration.
- Without Nuvio nothing of this runs. The adapter only couples to the reviewed Nuvio version (1.1.0-beta.7); other versions play normally in SDR. [Nuvio guide](docs/nuvio.md).

### Image changes and verification

- Derived from the verified r7 image with [`repack_image.py`](tools/repack_image.py) and a [declared change list](releases/r8-changes.json): four replaced entries (32-bit primary audio HAL, audio policy, Stremio bridge library, Stremio init script) and four added (media watchdog, Nuvio HDR adapter, its coupling script and the setup command). Every other entry keeps its contents and metadata; kernel, initrd, recovery and boot structures are unchanged. [Delta](releases/r8-image-delta.json).
- The HAL is built reproducibly from pinned sources by [`build.sh`](platform/next/audio-ac3/build.sh) (patch 0020); two clean builds gave identical bytes. Source for the other changes: patches [0021](platform/next/0021-stremio-bridge-delay-units.patch) and [0022](platform/next/0022-media-watch-and-nuvio-optin.patch).
- Fresh-data UEFI boot in QEMU/KVM: all r7 checks still pass; a 5.1 stream ran through a 6-channel mixer and the AC-3 encoder without audio-service crashes; the watchdog service runs and the setup command refuses cleanly without Nuvio. [Boot record](releases/r8-boot-validation.json).
- On the development NUC (LG TV, optical Logitech 5.1 system) the same files ran for several reboots: Dolby Digital on all six channels, clear centre dialogue, correct lip sync, sound restored by a display off/on cycle after an input switch (the step the watchdog automates), and Nuvio playing 4K HDR10 at 24 Hz with 5.1.
- The download helpers now fetch r8 by default. The r7 rescue kit works unchanged with r8 (same kernel).

**Test boundary:** the physical NUC runs the r8 files through a boot overlay on its development installation and was not reflashed with r8. HDMI receivers that take multichannel PCM directly were not tested; they now receive AC-3 as well. Nuvio is a third-party beta; only version 1.1.0-beta.7 was reviewed.

<a id="standby-and-app-stores"></a>

## Intel NUC Preview — Standby & App Stores

**Published 2026-10-14 · Home 1.1 · Android 16 / LineageOS 23.2**

[Download](https://github.com/zubSero/StremioBox/releases/tag/r7) · [Installation](docs/installation.md) · [Standby and apps](docs/standby-and-apps.md) · [Rescue system](docs/rescue.md) · [Validation](docs/testing.md#standby-and-app-stores-release)

![Home with Aurora Store and Flicky on the physical NUC](docs/assets/home-r7-app-stores.png)

### Fixed: the box no longer hangs after long standby

- SurfaceFlinger could wait forever while restoring the text console when a display was removed during standby or an HDMI change. The TV then showed No signal, the remote did nothing and only a power cycle helped.
- r7 ships the corrected SurfaceFlinger: it switches the console back to automatic mode first and waits at most 200 ms. This is the exact binary validated on the development NUC, equivalent to source patch 0018.

### Fixed: no scrolling text on the TV during standby

- The vendor files declared a fingerprint sensor the NUC does not have, so Android logged an error every second onto the console. During standby this looked like a boot loop.
- r7 replaces that feature file with an empty one. No functionality is lost.

### New: Aurora Store and Flicky

- Both stores are installed once on first boot and appear in Home under **Apps & settings**. Stremio stays the main action.
- Aurora Store 4.8.4 gives access to apps distributed through Google Play; Flicky 4.5.4 is a TV client for F-Droid. Both are unchanged signed APKs from F-Droid; their GPL source archives are attached to the release.
- Removing a store is permanent: first boot never installs it again. Existing r5/r6 users can install both APKs over ADB ([how](docs/adb-installation.md#add-the-app-stores-to-r5-or-r6)).

### New: optional rescue system

- A separate kit adds a small Alpine Linux system to the EFI partition with one boot menu entry. It runs from RAM, checks and mounts the Android partition and accepts SSH only with your own key. No keys or passwords are included. [Rescue guide](docs/rescue.md).

### Image changes and verification

- Derived from the verified r6 image with the new [`repack_image.py`](tools/repack_image.py) and a [declared change list](releases/r7-changes.json): three replaced and two added system entries. 19,579 other entries keep their contents and metadata; kernel, initrd, recovery and boot structures are unchanged. [Delta](releases/r7-image-delta.json).
- Fresh-data UEFI boot in QEMU/KVM: fixed SurfaceFlinger active, all three apps seeded with the expected hashes, no fingerprint feature, Home with both stores. Three virtual sleep/wake cycles kept the same SurfaceFlinger process without ANRs. [Boot record](releases/r7-boot-validation.json).
- The download helpers now fetch r7 by default.

**Test boundary:** the physical NUC runs the same five files from its development installation but was not reflashed with r7. The overnight standby test with the physical power button, a disk installation and complete app installation through each store are still pending. The rescue kit was tested in virtual machines only.

## Source candidate — 2026-10-13 (shipped in r7)

- Prepared patch 0018 for SurfaceFlinger console restoration: VT_AUTO before activation and bounded VT_GETSTATE polling instead of VT_WAITACTIVE. An equivalent exact-build native hotfix is active on the development NUC.
- Prepared product patch 0019 to seed Aurora Store 4.8.4 and Flicky 4.5.4 once, with pinned signed APK/source inputs. Existing installs, updates and later removals are preserved; Stremio remains the main Home action.
- Added opt-in next-release source preparation with input verification and transactional rollback. The published r5/r6 platform lock, image hashes, assets and default 17-port preparation path are preserved.
- Verified two reboots, three short Android sleep/wake cycles, two HDMI connector reconnect cycles and no new ANRs. Confirmed both stores in Home, Aurora onboarding, Flicky catalogue and idempotent first-boot seeding.
- Overnight physical Homatics standby, complete app installation through each store, full native source compilation and a new public ISO remain pending. [Details and test boundaries](docs/standby-and-apps.md).

## Download tooling update — 2026-10-06

- Added a Python-free Windows download ZIP with a double-click launcher and native PowerShell 5.1 helper.
- Added a Linux/macOS shell helper using curl and system SHA-256 tools; matching shell/JSON manifests are checked in CI.
- Added native-helper regression checks for corruption, wrong final hashes, invalid manifests, offline assembly and preservation of existing output.
- Documented a 7-Zip split-combination alternative, ADB app updates and the current limits of USB-free system installation.
- The installation ISO, Android platform and Home APK retain their original bytes. This changes how the release is downloaded, not the installed system.

<a id="english-home"></a>

## Intel NUC Preview — English Home

**Published 2026-10-05 · Home 1.1 · Android 16 / LineageOS 23.2**

[Download](https://github.com/zubSero/StremioBox/releases/tag/r6) · [Installation and existing-device update](docs/installation.md) · [Validation](docs/testing.md#english-home-update)

### Changed: the Home interface is English

- Replaced the Dutch Home heading, introductory text, app section, Settings label and app-unavailable message with English text. Home now shows “Movie night starts here.”, “Apps & settings” and “Settings”.
- Raised Home to **1.1 / version code 2**, signed with the existing release certificate. Android accepts it as an update to the original Home app.
- Included Home 1.1 in the installation image. New installations start with the English launcher.
- Published **`StremioBoxHome-1.1-en.apk`** for existing installations. Updating this APK changes Home without reinstalling Android.
- Replaced the public Home screenshot with a capture of the English interface running on the physical NUC.

### Image changes and verification

- Repacked the initial image with exactly **one changed system file**: `system/product/app/StremioBoxHome/StremioBoxHome.apk`.
- Verified **19,581 other system entries** retained their contents, permissions, ownership, extended attributes and symlink targets. Kernel, initrd, recovery, native playback code and boot artwork retain their previous hashes. [Filesystem delta](releases/r6-home-delta.json).
- Added the portable [`repack_home.py`](tools/repack_home.py) helper and exercised it on the published base image. It checks the input image, compares extracted filesystems and checks the rebuilt ISO's boot structures. [Repack instructions](docs/building.md#reproduce-the-english-home-delta-from-r5).
- Updated the download manifest and helper to retrieve the English image and verify both parts plus the reconstructed ISO.

### What was tested for this update

- Installed the signed Home update on the physical NUC, checked its version and visible English labels, rebooted, then checked that the update and labels persisted.
- Booted the final ISO through UEFI in a diskless QEMU/KVM guest with fresh Android data. Android completed boot, selected Home 1.1 and installed the original signed Stremio TV APK with the expected hash.
- Confirmed the English Home activity and guest screenshot. The VM's graphics has a red/blue channel swap; correct artwork colors and the public screenshot were checked on the physical Intel GPU. [Boot record](releases/r6-boot-validation.json).
- Verified published asset hashes and public download URLs.

**Test boundary:** the physical NUC received the Home app update; it was not reflashed with the new ISO. The full HDR/audio/Bluetooth acceptance matrix was not rerun for this launcher-only change. Native platform results below describe the same preserved binaries. The fresh-data VM test provisioned temporary guest settings to reach Home; it does not certify the complete setup wizard or disk installer.

### Upgrade guidance

Existing installations with Dutch Home can use the signed APK described in the [update guide](docs/installation.md#update-an-existing-installation). For a new installation, use this English image. The original public download remains available with Dutch Home 1.0 for traceability.

<a id="initial-release"></a>

## Intel NUC Preview — Initial Release

**Published 2026-10-05 · Home 1.0 · Android 16 / LineageOS 23.2**

[Historical download](https://github.com/zubSero/StremioBox/releases/tag/r5) · [Hardware](docs/hardware.md) · [Physical test report](docs/testing.md)

This was the first publicly downloadable image for the **Intel NUC10i5FNH**, with Intel UHD Comet Lake GT2 graphics, Intel AX201 Bluetooth, a Homatics B21 remote and an LG HDR TV. It packages platform fixes developed and tested before publication. Those fixes were already compiled into the development base; this release added Home, branding and clean first-boot app installation through a verified image repack.

### Video decoding, color and HDR10

- Integrated Intel's hardware video path for the tested HEVC Main10 stream. Android MediaCodec passes decoded 10-bit P010 buffers through the GPU rather than requiring software decoding for that case. [Codec output patch](platform/patches/0002-codec-native-p010.patch).
- Added Android 10-bit native visual support in Mesa and HDR10 capabilities, output mode and HDMI metadata handling in the display composer. The tested output carries BT.2020 color and PQ transfer information, and the LG TV reports HDR mode.
- Added stable identities for recycled hardware codec buffers to address stale buffer reuse in the rendering path. [Buffer identity patch](platform/patches/0016-codec-ahwb-buffer-identity.patch).
- Integrated the HDR surface helper with Stremio's existing mpv player. The ordinary controls and seek bar remain available.
- **Observed result:** 4K HEVC Main10 HDR10 playback around 24 fps with correct picture and audible sound confirmed on the test TV. This does not establish universal codec support or HDR support in every player.

### HDMI audio

- Configured HDMI as the primary output for the dedicated NUC TV product, resolving the no-sound behavior seen on the test setup. The x86 audio service otherwise tried to open an unavailable default speaker output. [Product configuration](platform/product/lineage_nuc10_tv.mk).
- Checked active Android AudioTrack output and advancing ALSA playback counters, with audible film sound confirmed before and after display standby.
- An AC3 5.1 source was used, but the test did not establish receiver bitstream passthrough or certification for surround formats.

### Bluetooth remote and display standby

- Included the Homatics power/wake key mapping and product-specific Bluetooth scan settings used on the Intel AX201 test system.
- Verified that ordinary Homatics keys reconnect after a full Android reboot without repeating the pairing-button combination.
- Changed the suspend service to avoid synthetic wake behavior that interfered with the TV power sequence. Display standby keeps Android, Bluetooth and playback processes running while the display is off. [Standby patch](platform/patches/0017-display-standby-no-synthetic-wake.patch).
- Checked film picture and sound recovery after synthetic Android sleep/wake commands, with confirmation on the physical TV. “No signal” can appear while HDMI output is off.
- A separate final-image test of repeated **physical Homatics power-button cycles** remains pending. True ACPI S3 suspend and HDMI-CEC were not validated.

### Subtitle state in Stremio

- Added synchronization between Stremio's subtitle selection and the mpv subtitle state. Disabled is applied to the player, including around subtitle-language and audio-track changes.
- Verified that disabling external SRT subtitles returns `sid=no` and removes the overlay. Eight Java regression cases passed during development.
- The packaged integration retains the original Stremio UI. Embedded formats and every stream combination are outside the completed test scope. [Subtitle helper source](platform/product/stremio/SubtitleSync.java).

### Boot persistence and app compatibility

- Packaged the player adapter, HDR/subtitle helpers, native patches and init services in the image so the integration is reapplied after boot.
- Added a compatibility check against the installed Stremio app's expected Java fields and native library layout before binding the adapter. An incompatible app layout is rejected instead of treated as supported.
- Checked a same-version reinstall of the original signed Stremio TV 1.10.4 APK: app data and compatible integration were retained. A deliberately incompatible test fixture was rejected.
- Enabled authenticated ADB on TCP 5555 at boot for maintenance. Each user authorizes their own host; personal trusted ADB keys are not included.

### Home, branding and first setup

- Added StremioBox Home 1.0 with D-pad navigation to Stremio, Android settings and installed apps. **This initial version used Dutch labels.**
- Added the StremioBox logo, blue/violet wallpaper, boot animation and ISO boot-menu artwork.
- Added first-boot installation of the original signed **Stremio TV 1.10.4 x86_64** APK after Android's package scan. Existing app data is preserved.
- Published a clean system image without personal accounts, Bluetooth bonds or configured content add-ons.

### Platform and build changes

The image includes **17 source patches**, published with the product overlay and pinned source manifest. In addition to playback and standby changes, these cover:

- Bounded SurfaceFlinger console-thread shutdown, composer service naming and a const-correct composer query.
- Configurable build concurrency, kernel tool paths, host memory limits, output-path handling and bootstrap environment fixes.
- ISO title/label parameters, preserving the relationship between the image volume label and boot-time root discovery.
- An upstream SQLite tokenizer bracket fix and a pre-generated source manifest for the read-only build sandbox.

See the [complete patch-by-patch inventory](platform/README.md) and [build guide](docs/building.md). The exported manifest has 1,216 pinned projects; applying the upstream proprietary-project filter produces the embedded 1,215-project manifest and its exact hash. A clean full Android build from the public repository remains pending.

### Validation at publication

| Check | Result and scope |
| --- | --- |
| HDR playback | 179.679 seconds; 12 displayed-frame drops, 0 decoder drops |
| Playback after standby | 173.506 seconds; 6 displayed-frame drops, 0 decoder drops; counters reset between samples |
| H.264 SDR | 640 × 360 sample for 4.458 seconds, 0 drops |
| Bluetooth after reboot | Ordinary Homatics keys worked without re-pairing |
| HDMI sound and standby recovery | Confirmed on the physical TV |
| Vulkan | Seven Skia UI frames rendered using the Intel driver; a smoke test, not conformance testing |
| Clean-data ISO boot | Diskless UEFI VM reached setup, Home and Stremio sign-in after app seeding |
| Download integrity | Two release parts reassembled with the public helper into the exact original ISO hash |

[Full methods and limitations](docs/testing.md) · [Image verification record](releases/r5-image-verification.json)

### Known limitations carried into the English Home release

- One physical hardware configuration is verified. Other NUCs, GPUs, Bluetooth adapters and remotes require reports and testing.
- Dolby Vision, HLG, AV1, 4K60, VLC, ExoPlayer, HDMI audio passthrough, HDMI-CEC, true S3 sleep and subscription-service DRM are unverified.
- Multi-hour playback/thermal tests, the separate physical power-button retest and destructive disk installation on a spare drive are pending.
- The preview uses permissive SELinux and userdebug maintenance access. There is no managed OTA channel or consumer security certification.
- Future Stremio versions need compatibility review; the packaged bridge does not guarantee support for arbitrary app updates.

<a id="development-base"></a>

## Development base before public release

Internal revisions `r1`–`r4` were working builds used to develop Intel decoding, HDR output, buffer handling, HDMI audio, Bluetooth, standby and subtitle/update integration. They are not public release choices. The native platform was compiled in `r4`; the first public image added the product interface, and the English Home release updated the launcher.

The record does not assign individual fixes to those private revision numbers without a published per-build evidence trail. The source patches and public image records above identify the shipped changes.
