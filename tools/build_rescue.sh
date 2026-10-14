#!/bin/sh
# SPDX-License-Identifier: MIT
# Build the StremioBox rescue kit from the pinned Alpine minirootfs and a verified StremioBox ISO.
# Linux x86_64 host, root, network access to the Alpine 3.24 repositories, xorriso, erofs-utils.
# Usage: sudo tools/build_rescue.sh alpine-minirootfs-3.24.2-x86_64.tar.gz StremioBox-...iso OUTPUT_DIR
set -eu
rootfs_sha=c5ca053cfe1d85c5b96dff8b9bc57045f7f184a30ffb6b65776409ca90388677
repo=$(cd "$(dirname "$0")/.." && pwd)
tarball=$1; iso=$2; out=$3
[ "$(id -u)" = 0 ] || { echo 'Run as root' >&2; exit 1; }
[ ! -e "$out" ] || { echo 'Output exists; refusing to overwrite' >&2; exit 1; }
echo "$rootfs_sha  $tarball" | sha256sum -c -
work=$(mktemp -d /tmp/stremiobox-rescue.XXXXXX)
cleanup() {
    for m in "$work/system" "$work/root/proc" "$work/root/sys" "$work/root/dev"; do
        mountpoint -q "$m" && umount "$m"
    done
    rm -rf "$work"
}
trap cleanup EXIT
root=$work/root
mkdir -p "$root" "$work/system"
tar -xzf "$tarball" -C "$root"
cp /etc/resolv.conf "$root/etc/resolv.conf"
mount -t proc proc "$root/proc"; mount -t sysfs sys "$root/sys"; mount --bind /dev "$root/dev"
chroot "$root" /sbin/apk add --no-cache $(grep -v '^#' "$repo/rescue/packages.txt")
chroot "$root" /sbin/apk info -v | sort > "$work/package-versions.txt"
umount "$root/proc" "$root/sys" "$root/dev"
rm -f "$root/etc/resolv.conf"
rm -rf "$root/var/cache/apk"/* "$root/etc/dropbear"/* "$root/root/.ssh"

# Kernel, modules and Wi-Fi firmware come from the same verified image, so versions always match.
xorriso -osirrox on -indev "$iso" -extract /kernel "$work/kernel" -extract /system.efs "$work/system.efs" >/dev/null 2>&1
fsck.erofs --extract="$work/container" "$work/system.efs" >/dev/null
mount -o loop,ro,noload "$work/container/system.img" "$work/system"
kver=$(ls "$work/system/system/lib/modules")
for module in drivers/net/ethernet/intel/e1000e/e1000e.ko drivers/net/wireless/intel/iwlwifi/iwlwifi.ko \
              drivers/net/wireless/intel/iwlwifi/mvm/iwlmvm.ko net/mac80211/mac80211.ko net/wireless/cfg80211.ko; do
    mkdir -p "$root/lib/modules/$kver/kernel/$(dirname $module)"
    cp "$work/system/system/lib/modules/$kver/kernel/$module" "$root/lib/modules/$kver/kernel/$module"
done
cp "$work/system/system/lib/modules/$kver"/modules.builtin* "$work/system/system/lib/modules/$kver"/modules.order "$root/lib/modules/$kver/"
mkdir -p "$root/lib/firmware"
cp "$work/system/system/vendor/firmware/intel/iwlwifi"/iwlwifi-QuZ-a0-hr-b0-*.ucode* "$root/lib/firmware/"
umount "$work/system"
chroot "$root" /sbin/depmod "$kver"

cp -a "$repo/rescue/root/." "$root/"
chmod 755 "$root/init" "$root/etc/rescue/"*.sh "$root/usr/bin/sb-"*
# Public image: no keys of any kind; the owner provides authorized_keys on the ESP.
[ -z "$(find "$root/etc/dropbear" "$root/root" -type f 2>/dev/null)" ]

mkdir -p "$out"
(cd "$root" && find . | sort | cpio -o -H newc --quiet -R 0:0 --reproducible) | gzip -9n > "$out/rescue.img"
cp "$work/kernel" "$out/kernel"
cp "$repo/rescue/enable-rescue.sh" "$repo/rescue/wifi.conf.example" "$repo/rescue/authorized_keys" "$out/"
cp "$work/package-versions.txt" "$out/"
cp "$repo/rescue/README.txt" "$out/"
(cd "$out" && sha256sum kernel rescue.img enable-rescue.sh wifi.conf.example > SHA256SUMS)
echo "Rescue kit written to $out"
cat "$out/SHA256SUMS"
