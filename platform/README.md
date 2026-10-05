# Platform overlay and ports

[Project](../README.md) · [Build guide](../docs/building.md)

`manifest.xml` is the unchanged 1,216-project pinned source-preparation export. `input-lock.json` records its hash, the 17 ports and additional upstream binary inputs. Upstream's build-manifest filter excludes the Silead proprietary firmware project; the filtered bytes exactly match the embedded 1,215-project manifest hash. See [the verification record](../releases/manifest-verification.json) and the build guide for the remaining clean-build scope.

`product/` installs at `device/local/nuc10_tv` in the full source tree. It includes the Stremio bridge, HDR/subtitle helpers, update guard, authenticated ADB init, GPU configuration, Home prebuilt and first-boot seeding service. The original signed Stremio APK is an external build input, supplied separately and verified by hash.

| Port | Upstream project | Purpose |
| --- | --- | --- |
| 0001 | frameworks/native | Bound console-thread shutdown instead of blocking SurfaceFlinger indefinitely |
| 0002 | external/stagefright-plugins | Native NV12/P010 codec output and Main10 handling |
| 0003 | external/drm_hwcomposer | HDR10 display metadata / output integration |
| 0004 | device/generic/x86_64_tablet | Dedicated NUC TV product inheritance |
| 0005 | external/mesa3d | Android 10-bit native visual support |
| 0006 | device/lineage/atv | Homatics power/wake key mapping |
| 0007 | build/soong | Lower-memory host build limits |
| 0008 | device/generic/x86_64_tablet | Configurable kernel/tool build jobs |
| 0009 | bootable/aaropa | ISO title/label parameters and root label relationship |
| 0010 | build/soong | Absolute output handling in test packages |
| 0011 | hardware/interfaces | Composer clone init naming |
| 0012 | build/soong | Stable bootstrap builder environment |
| 0013 | external/drm_hwcomposer | Const-correct headless query port |
| 0014 | frameworks/base | Upstream SQLite tokenizer bracket fix |
| 0015 | vendor/lineage | Pre-generated build manifest for a read-only sandbox |
| 0016 | external/stagefright-plugins | Stable hardware-buffer identity for recycled codec buffers |
| 0017 | system/hardware/interfaces | Display standby without synthetic wake |

The patch order matters. `tools/prepare_platform.py` validates project revisions and file hashes before applying ports to a clean checkout. The helper has not been exercised against a newly downloaded full source tree in this public setup; its unit tests cover the transactional preparation behavior with small fixture repositories.
