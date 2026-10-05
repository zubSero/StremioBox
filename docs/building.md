# Source preparation and builds

[Back to the project](../README.md) · [Platform ports](../platform/README.md) · [Launcher](../launcher/README.md)

## What this repository contains

The pinned source-preparation export, all 17 ports, the current product overlay, Home source, its signed prebuilt APK, boot animation, artwork and checksums. It is an overlay repository, not a mirror of the full Android source tree. Private signing keys, app data and workstation-specific deployment tools are excluded.

The r5 ISO was derived from the compiled r4 platform through a verified branding/launcher/app-seed delta. A clean full r5 build from this public repository has **not** been completed. The source lock contains 1,216 projects; the upstream `proprietary_` exclusion rule yields the embedded 1,215-project manifest and its exact recorded hash. The instructions below remain a preparation path for contributors, not a promise of an identical ISO.

## Host and storage

Use an x86_64 Linux host; development used Ubuntu 24.04 through WSL. A full Android checkout and build require hundreds of GB and considerable RAM. Keep source, output and temporary artifacts on a dedicated volume. A repository clone or ISO download does not need the full toolchain.

The product pins its own Clang/Rust revisions and limits kernel jobs to four. Mesa host wheel versions and hashes are recorded in [mesa-requirements.lock](../platform/host/mesa-requirements.lock); Python 3.12 matches those wheels. Nested Ninja was limited to two workers during the original build. A new host must also satisfy the upstream project's Linux build dependencies and legacy ncurses ABI requirements.

## Initialize the pinned source export

Install Google's Repo tool and the upstream Android build prerequisites. Keep the original manifest repository as the origin because the exported `github` remote uses a relative URL. Replace the example absolute paths with your own locations:

```sh
export STREMIOBOX_REPO=/absolute/path/to/StremioBox
mkdir -p /absolute/path/to/android-source
cd /absolute/path/to/android-source
repo init -u https://github.com/los-tv-x86/lineage_bass_android.git \
  -b 68ee2f807dff9bcde3901acd874c51f288d630ec
cp "$STREMIOBOX_REPO/platform/manifest.xml" .repo/manifests/stremiobox-r5.xml
repo init -m stremiobox-r5.xml
repo sync -c -j4
```

The public export includes upstream projects beyond this target. Do not silently prune or update projects and then describe the result as the original locked build.

## Verify and apply the overlay

Obtain the original signed **Stremio TV 1.10.4 x86_64 APK** from Stremio's official distribution. The product's app-seed contract requires SHA-256:

```text
3a9f86646ba18f4f11073dfbb01e10b1d4019e78d89ba58ec3de79f36f6cfc8c
```

A different APK requires reviewing both app seeding and the player compatibility guard; do not just change the hash.

```sh
python3 "$STREMIOBOX_REPO/tools/prepare_platform.py" \
  --source "$PWD" --stremio-apk /absolute/path/to/stremio.apk
# The first run checks and previews. Apply only to a fresh locked checkout:
python3 "$STREMIOBOX_REPO/tools/prepare_platform.py" \
  --source "$PWD" --stremio-apk /absolute/path/to/stremio.apk --apply
```

The helper validates all exported project revisions and patch hashes, rejects local changes in projects being patched, checks the APK, applies ports in order and copies the product to `device/local/nuc10_tv`. It rolls back its own patch applications if preparation fails. It does not resync repositories, install host packages or erase disks.

## Additional pinned inputs

[input-lock.json](../platform/input-lock.json) records SOF 2025.12.2, installer assets and public firmware/ID data. Fetch and verify them before building, preserving their notices. Their upstream integration and vendor layout must match the target; the public preparation helper does not download or wire these host/vendor inputs automatically.

Install Mesa's locked Python tools in a host venv with `pip install --require-hashes -r .../mesa-requirements.lock` using Python 3.12. Keep nested build parallelism bounded on low-memory hosts. Prepare `OUT_DIR/nuc-source-manifest.xml` from `repo manifest -r` before Soong runs, and compare its project revisions to the pinned export; port 0015 makes the build sandbox consume that pre-generated file.

## Build entry point

After host tools, firmware and installer inputs have been configured, the product entry is:

```sh
export OUT_DIR=/absolute/path/to/android-out
export SKIP_AG_DOWNLOADS=true
export NINJA_HIGHMEM_NUM_JOBS=1
export NUC_BUILD_LOW_MEMORY=1
export BUILD_USERNAME=stremiobox-builder
export BUILD_HOSTNAME=stremiobox-build
mkdir -p "$OUT_DIR"
source build/envsetup.sh
lunch lineage_nuc10_tv bp4a userdebug
repo manifest -r -o "$OUT_DIR/nuc-source-manifest.xml"
m -j4 iso_img
```

The lunch form above is the one used by the original pinned builder. This public entry point has not been rerun as a clean build with all host/vendor prerequisites. Record your output hashes and run the [validation matrix](testing.md) before distributing a new revision.

## Signing and reproducibility

Home's prebuilt APK is the r5 signed artifact. The private Home release key is deliberately excluded. Rebuilding Home with your own key is suitable for a fork, but does not produce an in-place signature-compatible update to the official prebuilt. Android itself remains an unofficial userdebug image; there is no production verified-boot or OTA signing service here.

A release source bundle contains this selected public tree and notices. It is not the old workstation backup and cannot reproduce private migration steps. The [roadmap](roadmap.md) tracks a complete clean source build, additional license inventory and installer validation. The exported/embedded manifest relationship has already been [verified](../releases/manifest-verification.json).
