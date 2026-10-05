#!/system/bin/sh
# SPDX-License-Identifier: Apache-2.0
set -eu
[ "$(getprop ro.vendor.nuc.product)" = 1 ]
[ ! -e /data/local/nuc-stremio-update/disabled ] || exit 0
export CLASSPATH=/system/framework/nuc_stremio_guard.jar
exec app_process /system/bin UpdateGuard watch
