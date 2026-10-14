#!/bin/sh
# SPDX-License-Identifier: MIT
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev 2>/dev/null
mkdir -p /dev/pts /run /tmp /mnt/esp /mnt/android
mount -t devpts devpts /dev/pts
mount -t tmpfs tmpfs /run
mount -t tmpfs tmpfs /tmp
mount -t efivarfs efivarfs /sys/firmware/efi/efivars 2>/dev/null
echo 1 > /proc/sys/kernel/printk
hostname stremiobox-rescue
ip link set lo up
modprobe -a e1000e iwlmvm 2>/dev/null
sleep 2
# The ESP is the FAT partition that holds this rescue image. The Android partition stays unmounted.
for dev in $(blkid -t TYPE=vfat -o device); do
    mount -t vfat "$dev" /mnt/esp 2>/dev/null || continue
    [ -f /mnt/esp/efi/rescue/rescue.img ] && break
    umount /mnt/esp
done
rescue=/mnt/esp/efi/rescue
for nic in /sys/class/net/e*; do
    [ -e "$nic" ] || continue
    ip link set "${nic##*/}" up && udhcpc -i "${nic##*/}" -b -S -x hostname:stremiobox-rescue >/dev/null 2>&1
done
if [ -f $rescue/wifi.conf ]; then
    for i in 1 2 3 4 5 6 7 8 9 10; do
        [ -e /sys/class/net/wlan0 ] && break
        sleep 1
    done
    wpa_supplicant -B -i wlan0 -c $rescue/wifi.conf >/dev/null 2>&1 &&
        udhcpc -i wlan0 -b -S -x hostname:stremiobox-rescue >/dev/null 2>&1
fi
# SSH only with keys the owner placed on the ESP; passwords are never accepted.
if [ -s $rescue/authorized_keys ]; then
    mkdir -p -m 700 /root/.ssh /etc/dropbear
    cp $rescue/authorized_keys /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
    # Keep one host key per device so the fingerprint stays stable between rescue starts.
    key=$rescue/dropbear_ed25519_host_key
    [ -s $key ] || dropbearkey -t ed25519 -f $key >/dev/null 2>&1
    cp $key /etc/dropbear/dropbear_ed25519_host_key
    chmod 600 /etc/dropbear/dropbear_ed25519_host_key
    dropbear -s -K 60 -r /etc/dropbear/dropbear_ed25519_host_key
fi
