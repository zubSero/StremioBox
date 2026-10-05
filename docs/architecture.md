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

## r5 derivation

The native Android platform was compiled in r4 with all 17 ports. r5 is a controlled image repack adding branding, Home, first-boot app seeding and boot-menu art. Its recorded delta checks unchanged files and metadata against r4. Publishing r5 does not imply that a second full platform compile occurred.

The preserved source-preparation manifest contains 1,216 pinned projects. The upstream build-manifest rule retained by port 0015 excludes lines containing `proprietary_`, removing the Silead firmware project from the embedded manifest. Applying that filter yields 1,215 projects and exactly the recorded image-manifest SHA-256. Repository validation checks this relationship; [the verification record](../releases/manifest-verification.json) identifies both inputs. A clean public full rebuild remains pending, and this repository does not claim byte-for-byte reproducibility of the ISO.

## r6 English Home delta

r6 replaces Home 1.0 with English Home 1.1 (version code 2), signed by the same release key. Its [full delta](../releases/r6-home-delta.json) identifies exactly one changed file and 19,581 preserved system entries. Kernel, initrd, recovery, native code, boot art and first-boot Stremio seeding remain the verified r5 inputs. The physical NUC can install Home 1.1 as a regular signed app update; a fresh r6 installation gets it directly from the system image.
