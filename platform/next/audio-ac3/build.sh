#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Builds the 32-bit x86 primary audio HAL with AC-3 bitstream output (patch 0020)
# outside the platform tree. Linux host with git, curl, unzip, make and cpio.
#
#   build.sh <device-libs> [work-dir]
#
# <device-libs> holds libcutils.so, libtinyalsa.so, libaudioutils.so and
# libexpat.so from the box's /system/lib (adb pull); they are only linked against.
set -eu
[ $# -ge 1 ] || { echo "usage: $0 <device-libs> [work-dir]" >&2; exit 2; }
libs=$(cd "$1" && pwd)
here=$(cd "$(dirname "$0")" && pwd)
patch=$here/../0020-libaudio-ac3-bitstream.patch
work=${2:-$PWD/audio-ac3-build}
mkdir -p "$work" && work=$(cd "$work" && pwd)
src=$work/src
mkdir -p "$src"

for lib in libcutils libtinyalsa libaudioutils libexpat; do
    [ -f "$libs/$lib.so" ] || { echo "missing $libs/$lib.so" >&2; exit 1; }
done

ndk=$work/android-ndk-r27c
if [ ! -x "$ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/clang" ]; then
    curl -fsSLo "$work/ndk.zip" https://dl.google.com/android/repository/android-ndk-r27c-linux.zip
    unzip -q "$work/ndk.zip" -d "$work"
    rm "$work/ndk.zip"
fi
bin=$ndk/toolchains/llvm/prebuilt/linux-x86_64/bin
cc=$bin/i686-linux-android30-clang

# fetch <dir> <url> <commit> [sparse paths...]
fetch() {
    dir=$src/$1 url=$2 commit=$3
    shift 3
    if [ ! -d "$dir/.git" ]; then
        git init -q "$dir"
        git -C "$dir" remote add origin "$url"
        if [ $# -gt 0 ]; then
            git -C "$dir" sparse-checkout set --no-cone "$@"
        fi
    fi
    if [ "$(git -C "$dir" rev-parse -q --verify HEAD || true)" != "$commit" ]; then
        git -C "$dir" fetch -q --depth 1 --filter=blob:none origin "$commit"
        git -C "$dir" checkout -q "$commit"
    fi
}
fetch libaudio https://github.com/android-generic/platform_hardware_libaudio.git \
    889952b9fb3330d54739f9a974b14dfec0f0893b
fetch libhardware https://github.com/LineageOS/android_hardware_libhardware.git \
    0c3e9e0fe76d30d32282c7e8fcdbddc393dc297b /include /include_all
fetch media https://github.com/LineageOS/android_system_media.git \
    d00e4bb7148a13b1fc66c34f8161a3622b1905d2 /audio/include /audio_utils/include /camera/include
fetch core https://github.com/LineageOS/android_system_core.git \
    eb2de7321317226bbc1951382b3171fa59bb4d1d /libcutils/include /libsystem/include /libutils/include
fetch tinyalsa https://github.com/LineageOS/android_external_tinyalsa.git \
    668606f51469a22c6c4cd6a7a6a0d74606b93ef9 /include
fetch logging https://github.com/LineageOS/android_system_logging.git \
    e63321648d4f2cb7c437bd615366e8f8765ad2bc /liblog/include
fetch expat https://github.com/libexpat/libexpat.git \
    2691aff4304a6d7e053199c205620136481b9dd1 /expat/lib
fetch ffmpeg https://github.com/FFmpeg/FFmpeg.git \
    9047fa1b084f76b1b4d065af2d743df1b40dfb56

git -C "$src/libaudio" checkout -q -- .
git -C "$src/libaudio" clean -qfd
git -C "$src/libaudio" apply "$patch"

# FFmpeg n8.1 reduced to the AC-3 encoder, static and position independent.
ff=$work/ffmpeg-ac3
if [ ! -f "$ff/lib/libavcodec.a" ]; then
    (
        cd "$src/ffmpeg"
        ./configure --prefix="$ff" \
            --target-os=android --arch=x86 --cpu=generic --enable-cross-compile \
            --cc="$cc" --ar="$bin/llvm-ar" --ranlib="$bin/llvm-ranlib" \
            --nm="$bin/llvm-nm" --strip="$bin/llvm-strip" \
            --enable-static --disable-shared --enable-pic --disable-x86asm \
            --disable-everything --disable-programs --disable-doc --disable-network \
            --disable-avformat --disable-avfilter --disable-avdevice --disable-swscale \
            --disable-swresample --disable-autodetect \
            --enable-encoder=ac3 \
            --extra-cflags="-fvisibility=hidden -O2 -ffile-prefix-map=$src=." >"$work/ffmpeg-configure.log"
        make -j"$(nproc)" >"$work/ffmpeg-make.log"
        make install >/dev/null
    )
fi

hal=$src/libaudio/hal
out=$work/audio.primary.x86.so
"$cc" -shared -fPIC -O2 -Wall -Wno-unused-variable -Wno-unused-parameter \
    -Wno-unused-function -Wno-unused-but-set-variable -Wno-gnu-designator \
    -DLOG_NDEBUG=1 -ffile-prefix-map="$src=." \
    -I"$src/libhardware/include" \
    -I"$src/media/audio/include" \
    -I"$src/media/audio_utils/include" \
    -I"$src/core/libcutils/include" \
    -I"$src/core/libsystem/include" \
    -I"$src/core/libutils/include" \
    -I"$src/logging/liblog/include" \
    -I"$src/tinyalsa/include" \
    -I"$src/expat/expat/lib" \
    -I"$ff/include" \
    "$hal/audio_hw.c" "$hal/audio_route.c" "$hal/ac3_spdif.c" \
    "$ff/lib/libavcodec.a" "$ff/lib/libavutil.a" \
    "$libs/libcutils.so" "$libs/libtinyalsa.so" "$libs/libaudioutils.so" "$libs/libexpat.so" \
    -llog -lm -ldl \
    -Wl,--exclude-libs,ALL -Wl,--no-undefined -Wl,-soname,audio.primary.x86.so \
    -Wl,--build-id=none -o "$out"
"$bin/llvm-strip" --strip-unneeded "$out"
cp "$src/libaudio/policy/audio_policy_configuration.xml" "$work/audio_policy_configuration.xml"
sha256sum "$out" "$work/audio_policy_configuration.xml"
