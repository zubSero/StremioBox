# Standby recovery and installing other apps

[Project](../README.md) · [Candidate sources](../platform/next/README.md) · [Testing](testing.md)

**Status: 2026-10-13.** The current public ISO is r6. The changes below are installed on the development NUC and prepared as source patches for the next image. They are not included in the r5/r6 downloads. No new installation ISO or portable system updater has been published for this change.

## Standby hang after hours or overnight

The NUC10i5FNH sometimes stayed powered on while the TV reported **No signal**. The Homatics power button and a USB keyboard could not restore output, and ADB became unavailable. A cold power cycle restored normal operation. Failure to reconnect the remote during this state does not establish that its Bluetooth bond was deleted.

Captured watchdog traces identified SurfaceFlinger blocked during ConsoleManagerThread destruction. The earlier console-thread exit fix did not cover the subsequent virtual-terminal restore: VT_WAITACTIVE could wait indefinitely after the thread responsible for acknowledging VT_PROCESS transitions had exited.

Patch 0018 switches the terminal back to VT_AUTO before VT_ACTIVATE, then polls VT_GETSTATE at most 20 times with 10 ms delays. It preserves the existing constructor's VT_PROCESS behavior and the remaining terminal cleanup. The intended power mode remains display standby with Android running; this does not add S3 suspend support.

On the development device, an exact-build native hotfix implements the same destructor change. A guarded initrd overlay activates it only against the verified original binary, and an original-compositor recovery boot entry remains available. This device-specific installation is not a portable patch for arbitrary SurfaceFlinger binaries. Low Power Standby was also disabled on this device to retain network access during the intended display-only standby; that setting is not yet a universal image policy.

| Check on the development NUC | Result |
| --- | --- |
| Two full reboots | Correct hotfix and store-seed payloads active after boot |
| Three Android sleep/wake cycles | Android and ADB responsive; compositor remained alive |
| Two DRM connector off/detect cycles | Output reconnected; four console-manager destructor calls completed |
| ANR count | No new ANRs during these checks |
| Hours or overnight with physical Homatics power button | Pending |
| Full source compilation and fresh public ISO | Pending |

If a public r5/r6 installation hangs, first check the TV input and HDMI connection. Try waking Android with the remote or USB keyboard. If neither restores output, a cold power cycle recovered the test NUC. Record elapsed standby time and whether ADB responds; do not repeatedly unpair the remote to diagnose an unresponsive system. Include redacted logs and hardware details in a bug report.

## Other apps, with Stremio kept prominent

Home already supports other installed apps in the secondary **Apps & settings** row. Android's package installer is available. The Android 16 image does not contain Google Play Store or Google Play services.

The candidate adds two optional stores, installed once on first boot:

| Store | Pinned version | Role |
| --- | --- | --- |
| Flicky (`app.flicky`) | 4.5.4 / 988, x86_64 | TV-oriented client for F-Droid apps |
| Aurora Store (`com.aurora.store`) | 4.8.4 / 76 | Access to apps distributed through Google Play |

Press Home, move to **Apps & settings**, and open a store. Complete its own first-use setup and choose an app suitable for Android TV and x86_64. Aurora onboarding has been opened but no account or terms were accepted during development testing. Flicky's browse screen and catalogue loaded. Installing an app through each store's complete user flow still needs verification.

Newly seeded stores receive permission to request app installations; Android still handles installation. Existing store packages retain their state and permissions. The one-time marker prevents reseeding after the user removes a store, and the script does not replace user updates or clear app data. The original signed Stremio app and its primary Home action remain intact.

These stores do not supply Google Play services, device certification or subscription-service DRM. Apps requiring those components may not work. Phone-oriented apps may need a mouse or keyboard. Installing other apps is supported by the launcher; compatibility depends on each app.

APK/source URLs, sizes, hashes, ABIs and GPL-3.0-or-later provenance are pinned in [candidate inputs](../platform/next/inputs.json). Both APKs were verified against official F-Droid repository metadata before installation. See the [candidate build instructions](building.md#next-release-candidate) to include them in a source build.
