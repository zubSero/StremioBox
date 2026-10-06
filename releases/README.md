# Release files

`r6.json` pins the ISO filename, byte count, SHA-256 and ordered download pieces. `r6-image-verification.json` retains selected public image checks. `source-lock.json` records the selected platform, launcher and branding input bytes. `manifest-verification.json` shows how upstream's proprietary-project filter produces the exact embedded source manifest.

Use the [native download ZIP](https://github.com/zubSero/StremioBox/releases/download/r6/StremioBox-r6-native-download.zip): double-click `Download-StremioBox.cmd` on Windows, or run `bash tools/download.sh --output downloads` on Linux/macOS. No Python is required. The helpers check every part and the final ISO independently. See [installation](../docs/installation.md) for offline assembly and the tested 7-Zip alternative. The older Python helper remains optional; historical release assets retain their original bytes.

The [r6 GitHub release](https://github.com/zubSero/StremioBox/releases/tag/r6) also contains a public source bundle, brand kit, Home APK and `SHA256SUMS`. Disk images remain release assets and are deliberately excluded from Git history.

Checksums detect corruption and identify these artifacts. They do not represent a separate publisher signature or production Android verified-boot signing.

`r6-home-delta.json` verifies the Home-only change against r5. Historical `r5.json` and its image record remain available for the unchanged original release.
