# Release files

`r5.json` pins the ISO filename, byte count, SHA-256 and ordered download pieces. `r5-image-verification.json` retains selected public image checks. `source-lock.json` records the selected platform, launcher and branding input bytes. `manifest-verification.json` shows how upstream's proprietary-project filter produces the exact embedded source manifest.

Use `python3 tools/download.py` from the repository root to fetch and reconstruct the image, or `--offline` to assemble already-downloaded pieces. The final ISO hash is checked independently of the part hashes.

The [r5 GitHub release](https://github.com/zubSero/StremioBox/releases/tag/r5) also contains a public source bundle, brand kit, Home APK and `SHA256SUMS`. Disk images remain release assets and are deliberately excluded from Git history.

Checksums detect corruption and identify these artifacts. They do not represent a separate publisher signature or production Android verified-boot signing.
