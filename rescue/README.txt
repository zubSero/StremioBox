StremioBox rescue kit (optional)

A small Alpine Linux system that lives on the EFI partition and runs from RAM.
Use it when Android no longer starts: check and mount the Android partition,
restore files, or copy logs - over SSH or on the TV with a keyboard.

Contents
  kernel              the StremioBox kernel (same as the ISO's /kernel)
  rescue.img          Alpine 3.24 userland, network drivers, no keys
  enable-rescue.sh    installs the kit on the EFI partition and adds a GRUB entry
  authorized_keys     put your SSH public key(s) here before installing
  wifi.conf.example   optional Wi-Fi settings for the rescue system
  package-versions.txt exact Alpine package versions (sources: https://pkgs.alpinelinux.org)

Install (from a computer with ADB connected to the box)
  1. Add your public key to authorized_keys (optional; without it SSH stays off).
  2. adb root
     adb push StremioBox-rescue-kit /data/local/tmp/
     adb shell sh /data/local/tmp/StremioBox-rescue-kit/enable-rescue.sh
  3. Restart and choose "StremioBox rescue system" in the boot menu.

Remove
  adb shell sh /data/local/tmp/StremioBox-rescue-kit/enable-rescue.sh --remove

Inside the rescue system
  sb-disk      check the Android partition and mount it on /mnt/android
  sb-android   restart into StremioBox
  Alt+F2       local root shell on the TV (physical access is trusted)
Without any login it restarts into Android after 15 minutes.

Documentation: https://github.com/zubSero/StremioBox/blob/main/docs/rescue.md
