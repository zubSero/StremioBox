#!/system/bin/sh
# SPDX-License-Identifier: Apache-2.0
# The official signed APK and its mpv library remain the package's originals.
set -eu
base=/data/local/nuc-stremio-update
payload=/system/lib64/nuc-stremio/libplayer.so
helper_payload=/system/framework/nuc_stremio_hdr.jar
guard=/system/framework/nuc_stremio_guard.jar
[ ! -e "$base/disabled" ] || exit 0
apk=$(pm path com.stremio.one | sed -n 's/^package://p' | head -n 1)
case "$apk" in /data/app/*/com.stremio.one-*/base.apk) ;; *) exit 0 ;; esac
lib=${apk%/*}/lib/x86_64
[ -f "$lib/libplayer.so" ] && [ -f "$lib/libmpv.so" ] || exit 0
stamp=$(stat -c %i "$apk")
check() { [ -f "$2" ] && [ "$(sha256sum "$2" | cut -d' ' -f1)" = "$1" ]; }
# The maintenance payload is supplied by the read-only OS image.
wrapper_sha=$(sha256sum "$payload" | cut -d' ' -f1)
helper_sha=$(sha256sum "$helper_payload" | cut -d' ' -f1)
guard_sha=$(sha256sum "$guard" | cut -d' ' -f1)
# Re-evaluate a previously rejected APK after the OS supplies a new adapter.
key="$apk:$stamp:$wrapper_sha:$helper_sha:$guard_sha"
helper=/data/data/com.stremio.one/files/nuc-hdr
# The guard may run before the app's first launch. Its private files directory
# must belong to the app, including its SELinux categories, before mkdir below.
files=${helper%/*}
uid=$(stat -c %u /data/data/com.stremio.one)
gid=$(stat -c %g /data/data/com.stremio.one)
mkdir -p "$files"
chown "$uid:$gid" "$files"
chmod 700 "$files"
restorecon "$files"
if [ "$(cat "$base/current" 2>/dev/null || true)" = "$key" ] &&
   [ -f "$base/approved.sh" ] && check "$wrapper_sha" "$lib/libplayer.so" &&
   check "$helper_sha" "$helper/hdr-bridge.jar"; then exit 0; fi
if [ "$(cat "$base/rejected" 2>/dev/null || true)" = "$key" ]; then exit 0; fi
original=$lib/libplayer.so
if check "$wrapper_sha" "$original"; then original=$lib/libplayer.nuc-original.so; fi
if ! CLASSPATH="$guard" app_process /system/bin UpdateGuard check "$apk" "$original" "$lib/libmpv.so" > "$base/compatibility.txt" 2>&1; then
    echo "$key" > "$base/rejected"
    echo 'Stremio update needs adapter review; original player retained.'
    exit 0
fi
[ "$(pm path com.stremio.one | sed -n 's/^package://p' | head -n 1)" = "$apk" ] || exit 1
if [ "$original" != "$lib/libplayer.nuc-original.so" ]; then
    cp -p "$original" "$lib/libplayer.nuc-original.so.new"
    chown system:system "$lib/libplayer.nuc-original.so.new"
    chmod 755 "$lib/libplayer.nuc-original.so.new"
    chcon u:object_r:apk_data_file:s0 "$lib/libplayer.nuc-original.so.new"
    mv "$lib/libplayer.nuc-original.so.new" "$lib/libplayer.nuc-original.so"
fi
mkdir -p "$helper"
cp "$helper_payload" "$helper/hdr-bridge.jar.new"
chown "$uid:$gid" "$helper" "$helper/hdr-bridge.jar.new"
chmod 700 "$helper"
chmod 444 "$helper/hdr-bridge.jar.new"
restorecon -R "$helper"
mv "$helper/hdr-bridge.jar.new" "$helper/hdr-bridge.jar"
was_running=$(pidof com.stremio.one || true)
if ! check "$wrapper_sha" "$lib/libplayer.so"; then mount -o bind "$payload" "$lib/libplayer.so"; fi
apk_sha=$(sha256sum "$apk" | cut -d' ' -f1)
player_sha=$(sha256sum "$lib/libplayer.nuc-original.so" | cut -d' ' -f1)
mpv_sha=$(sha256sum "$lib/libmpv.so" | cut -d' ' -f1)
{
    echo "approved_apk='$apk'"
    echo "approved_apk_sha='$apk_sha'"
    echo "approved_player_sha='$player_sha'"
    echo "approved_mpv_sha='$mpv_sha'"
    echo "approved_wrapper_sha='$wrapper_sha'"
    echo "approved_helper_sha='$helper_sha'"
    echo "approved_guard_sha='$guard_sha'"
} > "$base/approved.sh.new"
chmod 600 "$base/approved.sh.new"
mv "$base/approved.sh.new" "$base/approved.sh"
echo "$key" > "$base/current"
rm -f "$base/rejected"
sync
echo 'Stremio native HDR repair applied to ABI-compatible installation.'
if [ -n "$was_running" ] && [ "$original" = "$lib/libplayer.so" ]; then
    am force-stop com.stremio.one
    am start -n com.stremio.one/com.stremio.tv.MainActivity >/dev/null
    echo 'Restarted Stremio once to load its updated HDR adapter.'
fi
