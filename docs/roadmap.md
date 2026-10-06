# Roadmap

[Back to the project](../README.md)

The current Intel NUC preview includes English Home and the playback, audio, Bluetooth and subtitle fixes described in the [changelog](../CHANGELOG.md). The next priorities are repeatable installation, longer hardware testing and a full source build. Items below are not promised compatibility or delivery dates.

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
