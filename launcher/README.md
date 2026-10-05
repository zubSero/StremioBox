# StremioBox Home

A small, dependency-free Java Home app for Android TV. Package `local.stremiobox.home`, minimum API 26, target API 35, MIT licensed. It provides D-pad tiles for Stremio, settings and installed apps; the installed r5 labels are Dutch.

[Home screenshot](../docs/assets/home.png) · [Brand kit](../docs/branding.md)

## Build your own APK

Install a JDK, Android SDK platform 35 and Android SDK Build Tools. No Gradle build cache is needed. Set `ANDROID_SDK_ROOT` (or pass `--sdk`), then supply your own release keystore and alias. Keep the keystore out of this repository.

```sh
export STREMIOBOX_KEY_PASSWORD='your-keystore-password'
python3 tools/build_home.py --sdk "$ANDROID_SDK_ROOT"       --keystore /private/path/home.jks --alias your-alias --output out/Home.apk
```

The helper resolves `aapt2`, `d8`, `zipalign` and `apksigner` from the SDK, compiles resources and Java, aligns the APK, signs it with the supplied key and verifies the signature. Passwords are passed through environment variables; there is no embedded release key.

Your own signature cannot update the preinstalled r5 Home APK in place. Use a fork image containing your APK, or a separate test package on a development device. The shipped prebuilt at [platform/product/stremiobox/home/StremioBoxHome.apk](../platform/product/stremiobox/home/StremioBoxHome.apk) is the original r5 artifact. A fresh portable-toolchain build of the public helper is not yet a clean-image certification.
