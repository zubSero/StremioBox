# Changelog

## r5 — public preview

First public StremioBox release for the Intel NUC10i5FNH test configuration.

- Added StremioBox Home, branded boot art, wallpaper and ISO boot-menu identity.
- Added first-boot installation of the original signed Stremio TV 1.10.4 x86_64 app.
- Preserved the compiled r4 platform and 17 native source ports through a verified filesystem delta.
- Verified physical HDR10 hardware playback, HDMI sound, normal remote keys after reboot and recovery after display standby.
- Published selected sources, branding, image hashes, test scope and a verified split-ISO download helper.

r5 is a controlled repack of r4, not a new full Android platform compile. See [test limitations](docs/testing.md).

## r1–r4 — private development revisions

Iterative Android 16 platform builds and validation for Intel video, P010/HDR output, buffer reuse, HDMI audio, Bluetooth, standby and Stremio subtitle/update integration. These revisions are historical development inputs and are not public supported releases here.
