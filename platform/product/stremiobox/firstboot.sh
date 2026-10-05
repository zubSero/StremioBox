#!/system/bin/sh
# SPDX-License-Identifier: MIT
# Install the unchanged, signed app only on initial setup, after the PM scan.
# The installed package keeps its own private data and native library layout.
set -eu
[ "$(getprop sys.boot_completed)" = 1 ]
[ "$(getprop ro.product.system.name)" = lineage_nuc10_tv ]
state=/data/local/stremiobox
[ ! -L "$state" ] && [ -d "$state" ]
[ ! -e "$state/seed-completed" ] || exit 0
if [ -z "$(pm path com.stremio.one)" ]; then
    app=/system/etc/stremiobox/stremio.apk
    expected=3a9f86646ba18f4f11073dfbb01e10b1d4019e78d89ba58ec3de79f36f6cfc8c
    [ "$(sha256sum "$app" | cut -d ' ' -f 1)" = "$expected" ]
    pm install "$app"
fi
[ -n "$(pm path com.stremio.one)" ]
echo stremiobox-firstboot-v1 > "$state/seed-completed"
chmod 0600 "$state/seed-completed"
