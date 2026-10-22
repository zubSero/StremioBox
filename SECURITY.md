# Security policy

## Release posture

r8 is an unofficial hardware-specific preview, built as **userdebug with permissive SELinux**. It is not a hardened consumer appliance or a certified Android device. Authenticated ADB is started on TCP port 5555 for maintenance; keep the box on a trusted network and do not forward that port to the internet.

The clean release image does not carry developer ADB authorization keys, paired Bluetooth devices, user accounts, tokens or private Home signing keys. Initial setup and host authorization belong to the new owner.

The optional [rescue kit](docs/rescue.md) ships without keys or passwords. SSH starts only with public keys that the owner puts on the EFI partition, password logins are refused, and the host key is generated on the device. Anyone with physical access gets a local root shell on the TV (Alt+F2), as with any unlocked boot menu. This does not change the image's permissive development security posture.

## Updates

r8 is the current public preview; r5 to r7 remain available for traceability. There is no automatic security-update or managed OTA channel. Source patches and the bridge are version-dependent: a replacement OS image must carry the fixes, and a new Stremio native layout requires validation. The compatibility guard rejects the tested incompatible fixture; it is not a sandbox or a universal security boundary.

The optional NuvioTV adapter is only coupled to NuvioTV builds whose native player library matches a reviewed SHA-256; it runs inside the Nuvio app with that app's permissions. `stremiobox-nuvio-setup` runs as root over authenticated ADB only. It reads Stremio's local addon list, which can contain debrid keys, passes the URLs to Nuvio on the same box and prints only host names. With a Nuvio account, Nuvio itself syncs those addon URLs to its cloud.

## Reporting a vulnerability

Use this repository's **Security → Advisories → Report a vulnerability** private reporting feature. Describe the affected revision, impact and minimal reproduction. Do not publish private keys, tokens or another person's data in an issue. No response-time commitment or bounty program is offered.

Ordinary playback, hardware and installation problems belong in the regular issue forms, with sensitive logs redacted.
