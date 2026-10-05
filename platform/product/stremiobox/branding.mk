# SPDX-License-Identifier: MIT
PRODUCT_BRAND := StremioBox
PRODUCT_MODEL := StremioBox
PRODUCT_PACKAGES += StremioBoxHome stremiobox-firstboot
PRODUCT_COPY_FILES += \
    device/local/nuc10_tv/stremiobox/bootanimation.zip:$(TARGET_COPY_OUT_PRODUCT)/media/bootanimation.zip \
    device/local/nuc10_tv/stremiobox/stremio.apk:$(TARGET_COPY_OUT_SYSTEM)/etc/stremiobox/stremio.apk
