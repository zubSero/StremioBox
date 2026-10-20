# Troubleshooting

[Back to the project](../README.md) · [Rescue system](rescue.md) · [Report a bug](https://github.com/zubSero/StremioBox/issues/new?template=bug.yml)

## Quick reference

| Symptom | Useful first checks |
| --- | --- |
| No signal during standby | HDMI being off is expected while asleep. Press the remote's power key or a USB keyboard key. On r5/r6, failure to wake after hours is a known issue fixed in r7; see [standby recovery](standby-and-apps.md). |
| Scrolling text on the TV during standby | On r5/r6 this is fingerprint-service log spam on the console, not a reboot loop. r7 hides the non-existent fingerprint feature. See [console log spam](standby-and-apps.md#console-log-spam-during-standby). |
| Android does not reach Home | Wait three minutes on first boot. Then restart once. If it still fails, use the [rescue system](rescue.md) or boot the live USB to check the disk. |
| Black playback | Confirm the app version, codec, HDR format and whether Home still renders. The validated path is Stremio mpv with HEVC Main10 HDR10 on the tested Intel GPU. |
| No audio | Confirm HDMI is the active output and check TV volume/input. Record app audio track and whether the same issue happens with an SDR sample. |
| Remote requires pairing again | Separate initial pairing from reconnect failure; state whether it followed reboot, display standby or deep suspend. Record remote and Bluetooth adapter model. |
| Subtitles despite Disabled | Record embedded versus external subtitles, selected audio track and app version. Do not post private stream URLs or subtitle-service tokens. |
| A store app does not install or start | Check that the app supports Android TV or x86_64. Apps that need Google Play services or certified DRM may not work. Phone apps may need a mouse. |
| Vulkan “not supported” | Some feature-reporting apps test a different contract. r5 passed a specific Intel Skia UI smoke test, not every Vulkan conformance check. Name the reporting app and attach redacted output. |
| Download checksum failure | Rerun the helper; a corrupt part is rejected and a complete existing valid image is reused. Check free storage and use this release's matching manifest. |
| ADB unavailable | Use a trusted network, confirm the box address and authorize your own host key. First setup must have finished. Never publish your private ADB key. |

## Dialogue is quiet or the soundbar shows stereo

Up to r7 the NUC sends only stereo PCM over HDMI. If your TV reports only stereo LPCM and a soundbar or 5.1 system hangs on the TV's optical output, the system receives stereo instead of Dolby 5.1 and dialogue gets lost in the mix. Set the TV's digital audio output to Auto or Passthrough; the fix itself is a candidate for the next release, with a guarded install for running boxes: [5.1 through optical soundbars](../platform/next/audio-ac3/README.md).

The audio/subtitle sync option in the Stremio player froze the picture in r5–r7 (a unit error); the same candidate fixes it.

## Box stays dark after standby

1. Check the TV input and the HDMI cable; switch the TV input away and back.
2. Press the remote's power key, then a key on a USB keyboard.
3. Try `adb connect <box-address>:5555`. If ADB answers, Android is running: collect `adb logcat -d` and `adb shell ls /data/anr` before restarting.
4. If nothing responds, hold the NUC's power button for about five seconds and start it again.

Note how long the box was in standby and whether ADB answered. Do not unpair the remote to diagnose an unresponsive system.

## Collect logs for a report

```sh
adb connect <box-address>:5555
adb logcat -d > logcat.txt
adb shell dmesg > dmesg.txt
adb bugreport bugreport.zip
```

`adb shell dmesg` needs `adb root` first. Before posting, remove account names, e-mail addresses, serial numbers, MAC addresses, private network addresses, stream URLs and access tokens.

## Android no longer starts

1. Restart once; a single interrupted start is not unusual after a power loss.
2. With the [rescue kit](rescue.md) installed, choose **StremioBox rescue system** in the boot menu (hold Esc or Shift if it is hidden), then run `sb-disk` to check and mount the Android partition.
3. Without the kit, boot the StremioBox USB stick in **Try** mode. Live mode does not change the installed system.
4. Keep `/data` if you want to keep apps and settings. A reinstall that formats the partition removes them.

Include the revision, public hardware IDs, exact steps and expected/actual behavior in a report. Redact account identifiers, serials, MAC addresses, local/private network addresses, authentication links and access tokens from logs or screenshots.
