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

The preserved source-preparation manifest contains 1,216 pinned projects; the embedded image verification record reports a 1,215-project build manifest with a different hash. Both records are retained honestly. Resolving that difference and proving a clean rebuild are roadmap items; this repository does not claim byte-for-byte reproducibility of the ISO.
