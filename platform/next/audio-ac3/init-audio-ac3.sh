	# SPDX-License-Identifier: Apache-2.0
	# Boot overlay block for the Android-x86 initrd /init, inserted directly before
	# `exec ${SWITCH:-switch_root} $MODE_BASE /init`. Files live in
	# /NUCTV-A16/audio-ac3/ on the Android partition; create `disabled` there to skip.
	#
	# 5.1 audio for TVs that only take stereo LPCM: the primary HAL encodes the 5.1 mix as an
	# AC-3 bitstream. The HAL and its 5.1 policy are only used together, and only over the
	# exact originals. The Stremio bridge also converts its millisecond delay setting.
	if [ "$SRC" = /NUCTV-A16 ] || [ "$SRC" = NUCTV-A16 ]; then
	    _nuc_ac3=/mnt/$SRC/audio-ac3
	    _nuc_hal=/system/vendor/lib/hw/audio.primary.x86.so
	    _nuc_apc=/system/vendor/etc/audio_policy_configuration.xml
	    _nuc_bridge=/system/lib64/nuc-stremio/libplayer.so
	    if [ ! -e "$_nuc_ac3/disabled" ] && [ -f "$_nuc_ac3/audio.primary.x86.so" ] &&
	       [ -f "$_nuc_ac3/audio_policy_configuration.xml" ] &&
	       [ "$(stat -c %s "$_nuc_hal")" = 34880 ] && [ "$(stat -c %s "$_nuc_apc")" = 6441 ]; then
	        if mount --bind "$_nuc_ac3/audio.primary.x86.so" "$_nuc_hal"; then
	            if mount --bind "$_nuc_ac3/audio_policy_configuration.xml" "$_nuc_apc"; then
	                echo 'StremioBox: 5.1 AC-3 audio output enabled' > /dev/kmsg
	            else
	                umount "$_nuc_hal"
	            fi
	        fi
	    fi
	    if [ ! -e "$_nuc_ac3/disabled" ] && [ -f "$_nuc_ac3/libplayer.so" ] &&
	       [ "$(stat -c %s "$_nuc_bridge")" = 51432 ] &&
	       mount --bind "$_nuc_ac3/libplayer.so" "$_nuc_bridge"; then
	        echo 'StremioBox: Stremio delay fix enabled' > /dev/kmsg
	    fi
	fi
