# SPDX-License-Identifier: Apache-2.0
# NUC10 TV inherits the hardware tree directly, without its tablet product.
USE_TV_BUILD := true
NUC10_TV_BUILD := true
PRODUCT_IS_ATV := true
TARGET_ATV_FORCE_1080_SCALING := false
BOARD_IS_ZENITH_BUILD := true

$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, device/google/atv/products/atv_base.mk)
$(call inherit-product, device/generic/x86_64_tablet/device.mk)
$(call inherit-product, vendor/lineage/config/common_tv.mk)

# This flag tests presence, including the string "false". Clear it explicitly
# so the authenticated userdebug build supports adb root for maintenance.
PRODUCT_NOT_DEBUGGABLE_IN_USERDEBUG :=
PRODUCT_NAME := lineage_nuc10_tv
PRODUCT_DEVICE := nuc10_tv
PRODUCT_BRAND := NUC
PRODUCT_MODEL := NUC TV
PRODUCT_MANUFACTURER := Intel
PRODUCT_CHARACTERISTICS := tv
PRODUCT_AAPT_PREF_CONFIG := tvdpi

# Lineage's compat tree already supplies these same protobuf module names.
PRODUCT_SOURCE_ROOT_DIRS += -prebuilts/misc/protobuf_vendorcompat
# Qualcomm phone display trees require ARM-only vendor libraries, and are not
# used by this Intel product. Do not scan their incompatible Blueprint files.
PRODUCT_SOURCE_ROOT_DIRS += -hardware/qcom-caf
PRODUCT_SOURCE_ROOT_DIRS += -vendor/qcom
PRODUCT_SOURCE_ROOT_DIRS += -hardware/qcom

# Only the two properties already measured on this NUC's AX201 are adjusted.
# Firmware, pairing keys, privacy and Bluetooth PHY remain upstream defaults.
PRODUCT_VENDOR_PROPERTIES += \
    ro.vendor.nuc.product=1 \
    ro.vendor.nuc.hdr10=true \
    ro.vendor.nuc.p010_gpu_only=true \
    bluetooth.core.le.connection_scan_interval_slow=256 \
    bluetooth.core.le.connection_scan_window_slow=48

# SurfaceFlinger otherwise defaults to an SDR-only composition gamut, even
# when the composer advertises the connected display's HDR10 capability.
PRODUCT_SYSTEM_PROPERTIES += \
    ro.surface_flinger.has_wide_color_display=true

# NUC10 exposes only HDMI PCM devices. The x86 primary HAL otherwise rejects
# every device while opening the default Speaker output, leaving audio policy
# uninitialized. Select its existing HDMI path before audioserver starts.
PRODUCT_SYSTEM_PROPERTIES += hal.audio.primary.hdmi=true

PRODUCT_COPY_FILES += \
    device/local/nuc10_tv/init.nuc-adb.rc:$(TARGET_COPY_OUT_SYSTEM)/etc/init/init.nuc-adb.rc

# Source-built maintenance for the ordinary, separately installed signed app.
PRODUCT_PACKAGES += \
    libnuc_stremio_adapter \
    nuc_stremio_hdr \
    nuc_stremio_guard \
    nuc-stremio-guard \
    nuc-stremio-reconcile \
    nuc-stremio-boot-approved

# No Google services, translators, activation package or account data is added.

# Persistent StremioBox home and first-run app, revision5.
$(call inherit-product, device/local/nuc10_tv/stremiobox/branding.mk)
