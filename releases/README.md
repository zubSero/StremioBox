# Release files

`r9.json` pins the ISO filename, byte count, SHA-256 and ordered download pieces. `r9-image-verification.json` retains selected public image checks. `source-lock.json` records the selected platform, launcher and branding input bytes. `manifest-verification.json` shows how upstream's proprietary-project filter produces the exact embedded source manifest.

Use the [native download ZIP](https://github.com/zubSero/StremioBox/releases/download/r9/StremioBox-r9-native-download.zip): double-click `Download-StremioBox.cmd` on Windows, or run `bash tools/download.sh --output downloads` on Linux/macOS. No Python is required. The helpers check every part and the final ISO independently. See [installation](../docs/installation.md) for offline assembly and the tested 7-Zip alternative. The older Python helper remains optional; historical release assets retain their original bytes.

The [r9 GitHub release](https://github.com/zubSero/StremioBox/releases/tag/r9) also contains a public source bundle, the store APKs with their corresponding sources, the FFmpeg source for the audio HAL, the rescue kit, the r9 input files and `SHA256SUMS`. Disk images remain release assets and are deliberately excluded from Git history.

Checksums detect corruption and identify these artifacts. They do not represent a separate publisher signature or production Android verified-boot signing.

`r9-changes.json` declares the two fixes against r8 and `r9-image-delta.json` records them; `r9-boot-validation.json` records the virtual-machine checks. `r8-changes.json` declares the eight system changes against r7 and `r8-image-delta.json` records them; `r8-boot-validation.json` records the virtual-machine boot, audio, watchdog and Nuvio-command checks. `r7-changes.json` declares the five system changes against r6; `r7-image-delta.json` records them with before/after metadata. `r7-boot-validation.json` and `r7-rescue-validation.json` record the virtual-machine tests. `r6-home-delta.json` verifies the Home-only change from r5 to r6. Historical `r5.json`/`r6.json` and their image records remain available for the unchanged earlier releases.
