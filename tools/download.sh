#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Linux/macOS: Bash, curl and the system SHA-256 utility. No Python.
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
manifest="$root/releases/r6-download.txt"
output=downloads
offline=false
temporary=
while [ "$#" -gt 0 ]; do
    case "$1" in
        --output) output=$2; shift 2 ;;
        --manifest) manifest=$2; shift 2 ;;
        --offline) offline=true; shift ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done
fail() { echo "Error: $*" >&2; exit 1; }
cleanup() { if [ -n "$temporary" ]; then rm -f -- "$temporary"; fi; }
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
if command -v sha256sum >/dev/null 2>&1; then
    hash() { sha256sum "$1" | awk '{print $1}'; }
elif command -v shasum >/dev/null 2>&1; then
    hash() { shasum -a 256 "$1" | awk '{print $1}'; }
else
    fail 'A system SHA-256 utility is required.'
fi
names=(); sizes=(); hashes=()
release=; image=; image_size=; image_hash=
while read -r kind name size checksum extra; do
    case "$kind" in
        release)
            [ -z "$release" ] && [[ "$name" =~ ^[a-zA-Z0-9._-]+$ ]] &&
                [ -z "$size$checksum$extra" ] || fail 'Invalid release record.'
            release=$name ;;
        image|part)
            [[ "$name" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]*$ ]] &&
                [[ "$size" =~ ^[1-9][0-9]*$ ]] && [ "${#size}" -le 10 ] &&
                [[ "$checksum" =~ ^[0-9a-f]{64}$ ]] && [ -z "$extra" ] || fail 'Invalid asset record.'
            if [ "$kind" = image ]; then
                [ -z "$image" ] && [[ "$name" = *.iso ]] || fail 'Invalid image record.'
                image=$name; image_size=$size; image_hash=$checksum
            else
                names+=("$name"); sizes+=("$size"); hashes+=("$checksum")
            fi ;;
        *) fail 'Unsupported manifest record.' ;;
    esac
done < "$manifest"
[ -n "$release" ] && [ -n "$image" ] && [ "${#names[@]}" -gt 0 ] &&
    [ "${#names[@]}" -le 100 ] || fail 'Incomplete manifest.'
total=0
for ((i=0; i<${#names[@]}; i++)); do
    expected=$(printf '%s.%03d' "$image" "$((i+1))")
    [ "${names[$i]}" = "$expected" ] && [ "${sizes[$i]}" -lt 2147483648 ] || fail 'Invalid part sequence or size.'
    total=$((total + sizes[i]))
done
[ "$total" -eq "$image_size" ] || fail 'Part sizes do not match the image.'
mkdir -p -- "$output"
output=$(cd -- "$output" && pwd)
verify() {
    [ ! -L "$1" ] && [ -f "$1" ] && [ "$(wc -c < "$1" | tr -d ' ')" = "$2" ] &&
        [ "$(hash "$1")" = "$3" ] || fail "File is invalid; move it aside first: $1"
}
if [ -e "$output/$image" ] || [ -L "$output/$image" ]; then
    verify "$output/$image" "$image_size" "$image_hash"
    echo "ISO already verified: $output/$image"
    exit 0
fi
needed=$image_size
for ((i=0; i<${#names[@]}; i++)); do
    target="$output/${names[$i]}"
    if [ -e "$target" ] || [ -L "$target" ]; then
        verify "$target" "${sizes[$i]}" "${hashes[$i]}"
    elif "$offline"; then
        fail "Offline part is missing: $target"
    else
        needed=$((needed + sizes[i]))
    fi
done
available=$(df -Pk "$output" | awk 'END {print $4}')
[ "$available" -ge "$(((needed + 1023) / 1024))" ] || fail 'Insufficient free space.'
for ((i=0; i<${#names[@]}; i++)); do
    target="$output/${names[$i]}"
    if [ -e "$target" ] || [ -L "$target" ]; then
        verify "$target" "${sizes[$i]}" "${hashes[$i]}"
        continue
    fi
    temporary=$(mktemp "$output/stremiobox.XXXXXXXX")
    echo "Downloading: ${names[$i]}"
    curl --fail --location --proto '=https' --proto-redir '=https' --connect-timeout 30 \
        --speed-limit 1024 --speed-time 60 \
        "https://github.com/zubSero/StremioBox/releases/download/$release/${names[$i]}" -o "$temporary"
    verify "$temporary" "${sizes[$i]}" "${hashes[$i]}"
    ln "$temporary" "$target" || fail 'Cannot publish without overwriting; use a filesystem supporting hard links.'
    rm -f -- "$temporary"; temporary=
done
temporary=$(mktemp "$output/stremiobox.XXXXXXXX")
echo 'Assembling and verifying the ISO...'
for name in "${names[@]}"; do cat -- "$output/$name" >> "$temporary"; done
verify "$temporary" "$image_size" "$image_hash"
ln "$temporary" "$output/$image" || fail 'Cannot publish without overwriting; use a filesystem supporting hard links.'
rm -f -- "$temporary"; temporary=
echo "ISO verified: $output/$image"
echo "SHA-256: $image_hash"
