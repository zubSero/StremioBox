# How StremioBox fits together

[Back to the project](../README.md) · [Build guide](building.md)

## Home and first boot

`local.stremiobox.home` is a small Java Android TV Home app. Its D-pad tiles open Stremio, Android settings and installed apps. It is separate from video playback. The original signed Stremio app is installed only after Android's PackageManager has finished its first scan; existing user app data is preserved.

The product overlay sets StremioBox's brand/model, installs Home and packages the boot animation. The ISO boot menu uses the same art. The underlying disk label remains compatible with the root-discovery boot arguments.

## The video path

Stremio retains its ordinary mpv interface and controls. A native `libplayer` bridge and Java helpers adapt its existing rendering surface and subtitle state. The bridge delegates to the original player and mpv libraries instead of replacing the player UI.

For the tested HEVC Main10 HDR10 case, Android MediaCodec reaches Intel's VAAPI-backed codec service, carries 10-bit P010 buffers through the GPU and passes HDR10 information through DRM composer to HDMI. The stable hardware-buffer identity patch avoids confusing reused buffers; the composer and visual patches allow the matching 10-bit output.

This is a targeted integration, not a declaration that every application now supports every HDR format. VLC and ExoPlayer require their own validation.

## Boot and update guard

The adapter, helper JARs, init services and native fixes are installed in the system image. After each boot, reconciliation checks the signed app's expected native layout and helper compatibility before creating its private approval record and binding the adapter. The approval is generated on the device; it is not shipped with another user's data.

An incompatible app update fails the compatibility check. The tested same-version reinstall survives without losing app data. New Stremio versions need a deliberate review of the bridge contract, including private Java fields and native libraries.

## Standby and Bluetooth

Display standby keeps Android alive. The suspend-service patch removes synthetic wake behavior that interfered with the TV power sequence. The Homatics keymap and Bluetooth scan parameters are scoped to this TV product. True ACPI S3 suspend remains outside this release's tested behavior.

## Initial public image

The native Android platform was compiled in the development base (internal `r4`) with all 17 ports. **Intel NUC Preview — Initial Release** (`r5`) is a controlled image repack adding branding, Home, first-boot app seeding and boot-menu art. Its recorded delta checks unchanged files and metadata against that compiled base.

The preserved source-preparation manifest contains 1,216 pinned projects. The upstream build-manifest rule retained by port 0015 excludes lines containing `proprietary_`, removing the Silead firmware project from the embedded manifest. Applying that filter yields 1,215 projects and exactly the recorded image-manifest SHA-256. Repository validation checks this relationship; [the verification record](../releases/manifest-verification.json) identifies both inputs. A clean public full rebuild remains pending, and this repository does not claim byte-for-byte reproducibility of the ISO.

## English Home update

**Intel NUC Preview — English Home** (`r6`) replaces Home 1.0 with English Home 1.1 (version code 2), signed by the same release key. Its [full delta](../releases/r6-home-delta.json) identifies exactly one changed file and 19,581 preserved system entries. Kernel, initrd, recovery, native code, boot art and first-boot Stremio seeding remain the verified initial image's inputs. The physical NUC can install Home 1.1 as a regular signed app update; a fresh English Home installation gets it directly from the system image.

## 5.1 Surround Sound update

**Intel NUC Preview — 5.1 Surround Sound** (`r8`) replaces four system entries against r7 and adds four.

*Media watchdog (patch 0022).* `nuc-media-watch` starts after boot. Every five seconds it checks whether the TV still reports an ELD; when it is missing while the display is on and an ALSA playback stream runs, it cycles the display once so the TV reports it again. Once a minute it also runs `nuc-nuvio-hdr`.

*Optional NuvioTV (patch 0022).* NuvioTV loads its own mpv binding (`is.xyz.mpv.MPV`) from `libplayer.so`. `nuc-nuvio-hdr` keeps the app's original as `libplayer.nuvio-original.so` and bind-mounts `/system/lib64/nuc-stremio/libplayer-nuvio.so` over it, but only when the original's SHA-256 is on its reviewed list. The adapter forwards all 20 JNI methods, learns the mpv handle by redirecting the original's `mpv_create` import, and after each `loadfile` reads `video-params`/`video-dec-params`. For BT.2020/PQ/HLG video it tags the source (`vf format=gamma=pq…`), sets PQ/BT.2020 targets and recreates the GPU output; the EGL hook from `hdr-mpv-surface.c` then creates a 10-bit BT.2020 PQ window surface, and Android sends HDR10 to the display. `stremiobox-nuvio-setup` writes Nuvio's DataStore preferences and installs addons through Nuvio's `stremio://` install links.

*5.1 audio and sync.* The 32-bit primary audio HAL (patch 0020) now opens a 5.1 output; Android's mixer works in 5.1 and the HAL encodes each 32 ms as a Dolby Digital (AC-3) frame, wraps it in an IEC 61937 burst and plays that as stereo PCM with the IEC958 non-audio bit set. TVs that only accept stereo LPCM still decode or forward that bitstream, for example to an optical soundbar. The policy declares the 5.1 primary output. The Stremio bridge (patch 0021) converts Stremio's millisecond delay setting to mpv's seconds. [Details](../platform/next/audio-ac3/README.md) · [Full delta](../releases/r8-image-delta.json).

## Standby & App Stores update

**Intel NUC Preview — Standby & App Stores** (`r7`) changes five system entries against r6: SurfaceFlinger with the console-restore fix (patch 0018 behavior), the first-boot script and two store APKs (patch 0019), and an empty vendor fingerprint feature file. Everything else, including kernel, initrd and Home, keeps its r6 bytes. [Full delta](../releases/r7-image-delta.json). The first-boot service still installs Stremio first; the stores follow once, with a separate marker, so removing a store is permanent.

The optional [rescue system](rescue.md) is not part of the image. It runs the same kernel from the EFI partition with an Alpine userland in RAM and is added to GRUB as a separate entry.
