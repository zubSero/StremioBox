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
