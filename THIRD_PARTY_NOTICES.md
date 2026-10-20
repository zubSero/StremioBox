# Licenses, provenance and third-party notices

The root MIT license covers original repository tools, documentation, project branding and StremioBox Home. It does **not** relicense the Android platform, upstream patches, firmware, the original Stremio APK or other components in the ISO. Individual SPDX notices and upstream terms take precedence.

| Material | Origin / license scope |
| --- | --- |
| Home source and prebuilt | StremioBox; MIT, with the private signing key excluded |
| Original tools/docs/brand art | StremioBox; MIT; artwork AI-generated for the project |
| NUC product integration and player adapters | Files carrying `SPDX-License-Identifier: Apache-2.0`; [Apache license](LICENSES/Apache-2.0.txt) |
| Platform patch files | Changes to their named upstream projects; retain those projects' licenses and original notices |
| Android / LineageOS | [AOSP licenses](https://source.android.com/docs/setup/about/licenses) and each project's notices; source revisions in [the manifest](platform/manifest.xml) |
| Intel Mesa / drm_hwcomposer | Upstream Mesa and DRM composer licenses; patched revisions pinned in the manifest |
| Linux / Zenith kernel | Upstream kernel license terms, including GPL-2.0-only where applicable; kernel project and revision in the manifest |
| Intel media / SOF / firmware | Their original licenses and notices; input archives and hashes recorded in [input-lock.json](platform/input-lock.json) |
| Stremio TV APK | Original signed upstream distribution, unchanged; upstream terms apply; no ownership or blanket MIT grant claimed |
| mpv and codec libraries | Their original licenses, including GPL/LGPL components where applicable; packaged in their upstream distribution |
| AAROPA installer inputs | Upstream release assets and license notices; URLs/hashes recorded in input-lock.json |

## Source access

The platform source export identifies repositories and revisions. Modified source is supplied as 17 patches and the product overlay. [The build guide](docs/building.md) explains how to retrieve and prepare it, along with the manifest mismatch and clean-build limitations. Preserve all upstream license/notice files when making a new image or source distribution.

The public source bundle is an overlay plus pinned source references, not a full Android source mirror or a formal source offer for every upstream application binary. A full per-binary redistribution/source-compliance inventory remains a [roadmap item](docs/roadmap.md). Contributors distributing derivatives should check the applicable terms for their own binaries, especially GPL/LGPL components and firmware.

## Attribution

Thanks to LineageOS, los-tv-x86, AOSP, Android-x86, Android Generic, AAROPA, Mesa, drm_hwcomposer, Intel media/firmware contributors, Stremio and mpv. The project is independent and carries no official endorsement from them. Names and trademarks remain with their respective holders.

## Next-release app-store inputs

Aurora Store (AuroraOSS) and Flicky (mlm-games) retain **GPL-3.0-or-later** terms. Their APKs are unchanged signed distributions from F-Droid, used as external candidate build inputs. [Candidate inputs](platform/next/inputs.json) pin versions, ABI, APK hashes, source repositories and the exact corresponding source archives and hashes. Preserve those source archives and upstream license/notice files when distributing binaries. They are included in the r7 and r8 ISOs; the corresponding source archives are attached to the [r7](https://github.com/zubSero/StremioBox/releases/tag/r7) and [r8](https://github.com/zubSero/StremioBox/releases/tag/r8) releases. They are not part of the r5/r6 ISOs.

## AC-3 audio HAL (r8)

The r8 primary audio HAL (`/vendor/lib/hw/audio.primary.x86.so`) combines the android-generic `hardware/libaudio` HAL (Apache-2.0) with patch 0020 and a static, AC-3-encoder-only build of **FFmpeg n8.1** (libavcodec/libavutil), configured without `--enable-gpl` and therefore under **LGPL-2.1-or-later**. [`build.sh`](platform/next/audio-ac3/build.sh) pins every source and rebuilds the library from them, so the FFmpeg part can be modified and relinked. The exact FFmpeg source archive (`ffmpeg-n8.1-9047fa1b.tar.gz`) is attached to the [r8 release](https://github.com/zubSero/StremioBox/releases/tag/r8). Dolby and Dolby Digital are trademarks of Dolby Laboratories; StremioBox is not affiliated with or certified by Dolby.

## Rescue kit

The optional rescue kit contains Alpine Linux 3.24 packages (BusyBox, dropbear, e2fsprogs, dosfstools, util-linux, wpa_supplicant, iproute2, kmod, nano and dependencies) under their own licenses, mostly GPL-2.0, MIT and BSD. `package-versions.txt` in each kit lists the exact package versions; sources are available from [Alpine Linux](https://pkgs.alpinelinux.org/) and the [aports repository](https://gitlab.alpinelinux.org/alpine/aports). The kernel, its modules and Intel Wi-Fi firmware are copied unchanged from the StremioBox image. The kit's own scripts use MIT.
