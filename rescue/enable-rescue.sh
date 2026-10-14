#!/system/bin/sh
# SPDX-License-Identifier: MIT
# Install the StremioBox rescue system on the EFI system partition and add a GRUB entry.
# Run as root on the box from the extracted kit directory:
#   adb root && adb push StremioBox-rescue-kit /data/local/tmp/ &&
#   adb shell sh /data/local/tmp/StremioBox-rescue-kit/enable-rescue.sh
# Put your SSH public key(s) in the kit's authorized_keys file first to enable SSH.
# Use --remove to take the entry and files out again.
set -eu
kit=$(cd "$(dirname "$0")" && pwd)
esp=/mnt/stremiobox-esp
begin='# >>> StremioBox rescue >>>'
end='# <<< StremioBox rescue <<<'
[ "$(id -u)" = 0 ] || { echo 'Run as root (adb root first).' >&2; exit 1; }

mkdir -p $esp
cleanup() { umount $esp 2>/dev/null || true; }
trap cleanup EXIT
found=
for dev in /dev/block/nvme*p* /dev/block/sd[a-z][0-9]* /dev/block/mmcblk*p*; do
    [ -b "$dev" ] || continue
    mount -t vfat "$dev" $esp 2>/dev/null || continue
    if grep -l 'SRC=' $(find $esp -maxdepth 4 -iname grub.cfg 2>/dev/null) >/dev/null 2>&1; then
        found=$dev
        break
    fi
    umount $esp
done
[ -n "$found" ] || { echo 'No EFI partition with a StremioBox GRUB configuration was found; nothing changed.' >&2; exit 1; }
configs=$(grep -l 'SRC=' $(find $esp -maxdepth 4 -iname grub.cfg))
echo "EFI partition: $found"

if [ "${1:-}" = --remove ]; then
    for cfg in $configs; do
        sed -i "/^$begin\$/,/^$end\$/d" "$cfg"
        echo "Removed rescue entry from ${cfg#"$esp"}"
    done
    rm -rf $esp/efi/rescue
    sync
    echo 'Rescue system removed.'
    exit 0
fi

(cd "$kit" && sha256sum -c SHA256SUMS >/dev/null) || { echo 'Kit checksum mismatch; nothing changed.' >&2; exit 1; }
need=$(( $(stat -c %s "$kit/kernel") + $(stat -c %s "$kit/rescue.img") + 1048576 ))
free=$(( $(stat -f -c '%a * %S' $esp) ))
[ "$free" -gt "$need" ] || { echo "Not enough space on the EFI partition ($free bytes free); nothing changed." >&2; exit 1; }

mkdir -p $esp/efi/rescue
cp "$kit/kernel" $esp/efi/rescue/kernel.new && mv $esp/efi/rescue/kernel.new $esp/efi/rescue/kernel
cp "$kit/rescue.img" $esp/efi/rescue/rescue.img.new && mv $esp/efi/rescue/rescue.img.new $esp/efi/rescue/rescue.img
cp "$kit/wifi.conf.example" $esp/efi/rescue/
if [ -s "$kit/authorized_keys" ] && grep -Eq '^(ssh-|ecdsa-|sk-)' "$kit/authorized_keys"; then
    cp "$kit/authorized_keys" $esp/efi/rescue/authorized_keys
    echo 'SSH enabled with the keys from authorized_keys.'
else
    echo 'No public key in authorized_keys: SSH stays off (local console only).'
fi
for cfg in $configs; do
    if grep -qx "$begin" "$cfg"; then
        echo "Entry already present in ${cfg#"$esp"}"
        continue
    fi
    [ -e "$cfg.before-rescue" ] || cp "$cfg" "$cfg.before-rescue"
    cat >> "$cfg" <<ENTRY
$begin
menuentry 'StremioBox rescue system' --id stremiobox-rescue {
    search --no-floppy --file --set=root /efi/rescue/rescue.img
    linux /efi/rescue/kernel quiet loglevel=3 panic=10
    initrd /efi/rescue/rescue.img
}
$end
ENTRY
    echo "Added rescue entry to ${cfg#"$esp"} (backup: ${cfg#"$esp"}.before-rescue)"
done
sync
echo 'Done. Choose "StremioBox rescue system" in the boot menu (hold Esc or Shift during start-up if the menu is hidden).'
