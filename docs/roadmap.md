# Roadmap

[Back to the project](../README.md)

r5 is the first public snapshot of a working dedicated StremioBox installation. Future items below are priorities, not promised compatibility or delivery dates.

## Validate the existing release

- [ ] Retest the physical Homatics power button through repeated final-r5 cycles.
- [ ] Run multi-hour HDR playback and thermal/crash soak tests.
- [ ] Exercise the disk installer on a spare drive with recoverable partitions.
- [ ] Gather reproducible hardware reports for other Intel NUCs.

## Make the build repeatable

- [ ] Reconcile the exported 1,216-project source lock with the embedded 1,215-project image manifest.
- [ ] Complete and document a clean full public source build with pinned host/vendor inputs.
- [ ] Extend machine-readable third-party binary/license inventory and source-offer documentation.
- [ ] Define a release signing policy, rollback path and managed update channel.
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
