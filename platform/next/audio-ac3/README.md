# 5.1 sound through TVs with an optical soundbar

[Next-release candidate](../README.md) · [Troubleshooting](../../../docs/troubleshooting.md#dialogue-is-quiet-or-the-soundbar-shows-stereo)

## Problem

The x86 audio HAL sends stereo PCM to HDMI only. Many TVs report just 2-channel LPCM in their EDID, while they do decode or pass through Dolby Digital. With a soundbar or 5.1 system on the TV's optical output, the NUC therefore delivered stereo: the centre channel was folded into left and right and dialogue drowned in music and effects. A Chromecast on the same TV sounded fine because it sends a Dolby bitstream.

Stremio's mpv cannot pass bitstreams itself: its bundled FFmpeg is built without encoders and without the S/PDIF muxer.

## Change

| Part | Purpose |
| --- | --- |
| [0020](../0020-libaudio-ac3-bitstream.patch), hardware/libaudio | The primary output becomes 5.1. On HDMI the HAL encodes each 1536 frames to AC-3 at 640 kbit/s (FFmpeg n8.1 encoder, linked statically), wraps them as IEC 61937 bursts and sets the IEC958 non-audio bit. Other routes, or `vendor.audio.nuc.ac3=false`, get a dialogue-friendly stereo downmix. |
| [0021](../0021-stremio-bridge-delay-units.patch), product/stremio | Stremio passes its audio and subtitle delay in milliseconds, mpv expects seconds. A 100 ms tweak became 100 s and froze the picture. The bridge converts the unit. Its optional `audio.conf` override no longer forces any default. |
| [init-audio-ac3.sh](init-audio-ac3.sh) | Boot overlay block used on the development NUC until a source image ships. Binds the files only over the exact originals and only HAL and policy together. |

Every app benefits: anything that plays 5.1 PCM reaches the receiver as real 5.1, and stereo stays on the front speakers.

## Build

`build.sh` builds the 32-bit HAL outside the platform tree from pinned sources: android-generic libaudio, LineageOS 23.2 headers, expat and FFmpeg n8.1, with NDK r27c. Copy `libcutils.so`, `libtinyalsa.so`, `libaudioutils.so` and `libexpat.so` from the box's `/system/lib` first; they are only linked against.

```sh
adb pull /system/lib/libcutils.so libs/   # likewise for the other three
sh platform/next/audio-ac3/build.sh libs work
```

The audio HAL service on the NUC is 32-bit and loads `/vendor/lib/hw/audio.primary.x86.so`; the 64-bit copy is unused.

## Install on a running box (development layout)

1. Copy `audio.primary.x86.so`, `audio_policy_configuration.xml` and the rebuilt bridge `libplayer.so` to `/NUCTV-A16/audio-ac3/` on the Android partition. Label them `vendor_file`, `vendor_configs_file` and `system_lib_file`.
2. Add `init-audio-ac3.sh` to the initrd `/init` before the final `switch_root`, append it as an extra gzip cpio and keep a copy of the old initrd.
3. Reboot. `dmesg` shows `StremioBox: 5.1 AC-3 audio output enabled`.

Undo: create `/NUCTV-A16/audio-ac3/disabled` (also from the [rescue system](../../../docs/rescue.md)) or restore the previous initrd.

## Limits

- While enabled, all HDMI audio is AC-3. Stereo sources play on the front speakers unless the receiver upmixes.
- About 37 ms of encoder delay is added and reported to Android.
- TrueHD, DTS-HD and Atmos are decoded and re-encoded as 5.1 AC-3, which is also the maximum of an optical link.
- Shipped in r8 as a verified repack; not yet built in-tree in a full source build. See [verification.json](verification.json).
