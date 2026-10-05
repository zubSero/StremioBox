# SPDX-License-Identifier: Apache-2.0
include device/generic/x86_64_tablet/BoardConfig.mk

# Keep a software fallback, while avoiding unrelated GPU driver builds.
BOARD_GPU_DRIVERS := iris
BOARD_MESA3D_GALLIUM_DRIVERS := iris llvmpipe
BOARD_MESA3D_VULKAN_DRIVERS := intel swrast
# Intel video decoding is supplied by the selected iHD_drv_video package.
# Mesa's VA tracker does not support iris or llvmpipe.
BOARD_MESA3D_GALLIUM_VA := disabled

# The reference uses display standby. Automatic S3 is not yet accepted.
BOARD_KERNEL_CMDLINE += SLEEP_STATE=none FFMPEG_CODEC2_DRM=1
BOARD_KERNEL_CMDLINE += GRALLOC=minigbm HWC=drm_minigbm

# Generate an honest product fingerprint instead of upstream's Fugu spoof.
BUILD_FINGERPRINT :=
BOARD_VENDOR_SEPOLICY_DIRS += device/local/nuc10_tv/sepolicy

# Soong's recovery image DPI parser does not recognize the TV's "tvdpi".
# The TV app resources retain tvdpi; recovery gets the same numeric density.
TARGET_RECOVERY_DENSITY := 213
TARGET_SCREEN_DENSITY := 213

# Locked platform prebuilts pass this kernel's rust_is_available.sh check.
TARGET_CLANG_PATH := prebuilts/clang/host/linux-x86/clang-r547379/bin
TARGET_RUST_PATH := prebuilts/rust/linux-x86/1.88.0/bin
TARGET_BINDGEN_PATH := prebuilts/clang-tools/linux-x86/bin
KBUILD_JOBS := 4

# The public installer supports a distinct title and installation directory.
RELEASE_OS_TITLE := NUCTV
SHORTEN_RELEASE_OS_TITLE := NUCTV
RELEASE_ISO_PREFIX := nuc-tv
INSTALL_PREFIX := NUCTV
# Repo may write user/config caches; package the pinned manifest prepared outside
# the action sandbox rather than running Repo from its read-only namespace.
LINEAGE_BUILD_MANIFEST_FILE := $(OUT_DIR)/nuc-source-manifest.xml
