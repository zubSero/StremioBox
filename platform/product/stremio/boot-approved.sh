#!/system/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Restore only an exact installation already verified against its signed APK.
set -eu
# A bind mount during the boot package scan prevents native library extraction.
[ "$(getprop sys.boot_completed)" = 1 ] || exit 0
base=/data/local/nuc-stremio-update
payload=/system/lib64/nuc-stremio/libplayer.so
helper_payload=/system/framework/nuc_stremio_hdr.jar
guard=/system/framework/nuc_stremio_guard.jar
[ ! -e "$base/disabled" ] && [ -f "$base/approved.sh" ] || exit 0
. "$base/approved.sh"
case "$approved_apk" in /data/app/*/com.stremio.one-*/base.apk) ;; *) exit 0 ;; esac
lib=${approved_apk%/*}/lib/x86_64
check() { [ -f "$2" ] && [ "$(sha256sum "$2" | cut -d' ' -f1)" = "$1" ]; }
# An OS adapter update must pass the new guard before being injected again.
check "${approved_wrapper_sha:-}" "$payload" || exit 0
check "${approved_helper_sha:-}" "$helper_payload" || exit 0
check "${approved_guard_sha:-}" "$guard" || exit 0
check "$approved_apk_sha" "$approved_apk" || exit 0
check "$approved_player_sha" "$lib/libplayer.so" || exit 0
check "$approved_player_sha" "$lib/libplayer.nuc-original.so" || exit 0
check "$approved_mpv_sha" "$lib/libmpv.so" || exit 0
helper=/data/data/com.stremio.one/files/nuc-hdr/hdr-bridge.jar
# An OS update can change our helper. The runtime guard will reconcile it.
helper_sha=$(sha256sum "$helper_payload" | cut -d' ' -f1)
check "$helper_sha" "$helper" || exit 0
mount -o bind "$payload" "$lib/libplayer.so"
