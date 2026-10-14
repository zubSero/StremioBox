#!/bin/sh
# SPDX-License-Identifier: MIT
# Status on the TV. Without any login, the box returns to Android after 15 minutes.
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
while :; do
    clear
    printf '\n  StremioBox rescue system\n\n'
    ip -4 -br addr | grep -v '^lo' | sed 's/^/  /'
    if pidof dropbear >/dev/null; then
        printf '\n  From your computer:  ssh root@<IP>  (key from efi/rescue/authorized_keys)\n'
        printf '  Host key: %s\n' "$(dropbearkey -y -f /etc/dropbear/dropbear_ed25519_host_key 2>/dev/null | sed -n 's/^Fingerprint: //p')"
    else
        printf '\n  SSH is off: no efi/rescue/authorized_keys on the ESP.\n'
    fi
    printf '  Local shell: Alt+F2.  Back to Android: sb-android\n'
    [ "$(pidof dropbear | wc -w)" -gt 1 ] && touch /run/stay
    if [ ! -e /run/stay ] && [ "$(cut -d. -f1 /proc/uptime)" -gt 900 ]; then
        printf '\n  No login: restarting into Android.\n'
        sleep 5
        sb-android
    fi
    sleep 5
done
