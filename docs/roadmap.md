# Roadmap

[Back to the project](../README.md)

The current Intel NUC preview (r8) includes 5.1 Dolby Digital output, the standby fix, optional app stores, English Home and the playback, audio, Bluetooth and subtitle fixes described in the [changelog](../CHANGELOG.md). The next priorities are repeatable installation, longer hardware testing and a full source build. Items below are not promised compatibility or delivery dates.

## 5.1 audio

- [x] Find why dialogue drowned through an optical soundbar: the HAL sent only stereo PCM to a TV that accepts Dolby bitstreams.
- [x] Encode the 5.1 mix as AC-3 in the 32-bit primary HAL (patch 0020), with a reproducible out-of-tree build; validate Dolby 5.1, centre dialogue and lip sync on the development NUC.
- [x] Fix Stremio's millisecond audio/subtitle delay reaching mpv as seconds (patch 0021).
- [x] Publish r8 as a verified repack of r7 with a QEMU boot and 5.1 stream check.
- [ ] Build patch 0020 in-tree against `external/ffmpeg` in a full source build.
- [ ] Optional automatic switch to PCM stereo for stereo-only content; settings toggle for receivers that accept multichannel PCM.
- [x] Restore HDMI audio automatically when the TV drops its ELD after an input switch.

## Optional NuvioTV

- [x] HDR10 output for NuvioTV's libmpv engine through a reviewed-version adapter; settings and addon migration command.
- [ ] Review new NuvioTV releases and extend the adapter's reviewed list.
- [ ] Platform fix so ExoPlayer can show 4K 10-bit video (P010 buffers for the compositor), which would also help other apps.

## Standby recovery and optional app stores

- [x] Identify the SurfaceFlinger VT restore deadlock and prepare source patch 0018.
- [x] Validate an equivalent exact-build hotfix across reboots, short standby and HDMI reconnect on the development NUC.
- [x] Prepare one-time Aurora Store/Flicky seeding with pinned signed APKs and corresponding sources; verify Home visibility, store UI and reboot persistence.
- [ ] Complete hours/overnight standby using the physical Homatics power button.
- [ ] Complete app installation through both stores with the remote.
- [x] Publish r7: a verified repack of r6 with the validated compositor binary, store seeding and the hidden fingerprint feature; fresh-data UEFI boot and virtual sleep/wake checked.
- [x] Publish an optional, keyless rescue kit on the EFI partition, tested in QEMU/KVM including GRUB activation and removal.
- [ ] Flash r8 on the physical NUC and repeat the hardware acceptance matrix.
- [ ] Build the candidate platform from source and confirm the compiled SurfaceFlinger matches the validated behavior.
- [ ] Automatic fallback to the rescue system after failed starts in the public image (works on the development NUC).

See [standby and app support](standby-and-apps.md) and the [rescue system](rescue.md).

## Validate the existing release

- [ ] Retest the physical Homatics power button through repeated cycles on the public platform.
- [ ] Run multi-hour HDR playback and thermal/crash soak tests.
- [ ] Exercise the disk installer on a spare drive with recoverable partitions.
- [ ] Gather reproducible hardware reports for other Intel NUCs.

## Simplify installation

- [x] Provide Python-free local ISO assembly: a double-click Windows launcher, native PowerShell and a Linux/macOS shell helper, with matching manifests and SHA-256 verification.
- [ ] Offer one direct ISO download from a project-controlled release mirror to avoid split downloads altogether.
- [ ] Validate the USB installation path on a spare disk and document the first-start flow.
- [ ] Build and test a portable root-ADB installation/update package for supported existing Android layouts.
- [ ] Validate an internal-disk installation path from Linux and a network-boot package for users without removable media. See [USB-free options](without-usb.md).

## Make the build repeatable

- [x] Verify that upstream's proprietary-project filter maps the 1,216-project source lock to the embedded 1,215-project manifest, with an exact SHA-256 match.
- [ ] Complete and document a clean full public source build with pinned host/vendor inputs.
- [ ] Extend machine-readable third-party binary/license inventory and source-offer documentation.
- [ ] Define a release signing policy, rollback path and managed update channel.
- [ ] Publish and test a portable root-ADB system updater with disk/boot-layout checks, verified staging and recovery. The [ADB guide](adb-installation.md) distinguishes the tested Home update from the private development deployment.
- [ ] Move appropriate native fixes upstream to reduce local patch maintenance.

## Broaden playback and hardware checks

- [ ] Validate VLC and ExoPlayer independently.
- [ ] Test 4K60, additional codecs/profiles, audio passthrough and HDR formats where hardware permits.
- [ ] Investigate HDMI-CEC and true suspend/wake without losing Bluetooth recovery.
- [ ] Review compatibility for each new Stremio version before updating the app seed.

## Product polish

- [ ] Offer additional Home languages and accessibility settings.
- [ ] Move beyond permissive userdebug security for a future consumer-oriented build.

Ideas and hardware reports are welcome through [Discussions](https://github.com/zubSero/StremioBox/discussions) and [Issues](https://github.com/zubSero/StremioBox/issues).
