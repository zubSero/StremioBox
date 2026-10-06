# SPDX-License-Identifier: MIT
# Native Windows PowerShell 5.1+ downloader. No Python or administrator access.
[CmdletBinding()]
param(
    [string]$OutputDirectory = 'downloads',
    [string]$Manifest = '',
    [switch]$Offline
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Assert-Manifest($Data) {
    if ($Data.schema -ne 1 -or $Data.project -cne 'StremioBox' -or
        $Data.release -cnotmatch '^[a-zA-Z0-9._-]+$') { throw 'Unsupported manifest.' }
    if ($Data.parts -isnot [array] -or $Data.parts.Count -lt 1 -or $Data.parts.Count -gt 100) {
        throw 'Invalid part list.'
    }
    foreach ($spec in @($Data.image) + $Data.parts) {
        if ($spec.name -cnotmatch '^[a-zA-Z0-9][a-zA-Z0-9._-]*$' -or
            ($spec.bytes -isnot [int] -and $spec.bytes -isnot [long]) -or
            $spec.bytes -le 0 -or $spec.sha256 -cnotmatch '^[0-9a-f]{64}$') {
            throw 'Invalid asset filename, size or checksum.'
        }
    }
    if (-not $Data.image.name.EndsWith('.iso')) { throw 'Expected an ISO image.' }
    $base = 'https://github.com/zubSero/StremioBox/releases/download/' + $Data.release + '/'
    [long]$total = 0
    for ($i = 0; $i -lt $Data.parts.Count; $i++) {
        $part = $Data.parts[$i]
        if ($part.name -cne ($Data.image.name + ('.{0:000}' -f ($i + 1))) -or
            $part.url -cne ($base + $part.name) -or $part.bytes -ge 2147483648) {
            throw 'Unexpected part name, release URL or size.'
        }
        $total += $part.bytes
    }
    if ($total -ne $Data.image.bytes) { throw 'Part sizes do not match the image.' }
}

function Assert-File([string]$Path, $Spec) {
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
        $item.Length -ne $Spec.bytes -or
        (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $Spec.sha256) {
        throw "Existing file is invalid; move it aside first: $Path"
    }
}

function Copy-Bytes($Source, $Destination, [long]$Limit) {
    $buffer = New-Object byte[] (4 * 1024 * 1024)
    [long]$count = 0
    [long]$nextProgress = 128 * 1024 * 1024
    while (($read = $Source.Read($buffer, 0, $buffer.Length)) -gt 0) {
        $count += $read
        if ($count -gt $Limit) { throw 'Input exceeds the expected size.' }
        $Destination.Write($buffer, 0, $read)
        if ($count -ge $nextProgress) {
            Write-Host ('  {0:P0}' -f ($count / $Limit))
            $nextProgress += 128 * 1024 * 1024
        }
    }
    if ($count -ne $Limit) { throw 'Input is incomplete.' }
}

function Save-Part($Part, [string]$Folder) {
    $target = Join-Path $Folder $Part.name
    if (Test-Path -LiteralPath $target) { Assert-File $target $Part; return }
    if ($Offline) { throw "Offline part is missing: $target" }
    $temporary = Join-Path $Folder ([guid]::NewGuid().ToString() + '.partial')
    $destination = $null
    $response = $null
    $source = $null
    try {
        Write-Host ('Downloading: ' + $Part.name)
        $request = [Net.HttpWebRequest]::Create($Part.url)
        $request.UserAgent = 'StremioBox-native-download/1'
        $request.Timeout = 60000
        $request.ReadWriteTimeout = 60000
        $response = $request.GetResponse()
        $source = $response.GetResponseStream()
        $destination = [IO.File]::Open($temporary, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
        Copy-Bytes $source $destination $Part.bytes
        $destination.Dispose()
        $destination = $null
        Assert-File $temporary $Part
        [IO.File]::Move($temporary, $target)
        Write-Host ('Verified: ' + $Part.name)
    } finally {
        if ($null -ne $destination) { $destination.Dispose() }
        if ($null -ne $source) { $source.Dispose() }
        if ($null -ne $response) { $response.Dispose() }
        if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) }
    }
}

if (-not $Manifest) { $Manifest = Join-Path (Split-Path $PSScriptRoot -Parent) 'releases/r6.json' }
$data = Get-Content -LiteralPath $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
Assert-Manifest $data
$folder = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputDirectory)
[IO.Directory]::CreateDirectory($folder) | Out-Null
$image = Join-Path $folder $data.image.name
if (Test-Path -LiteralPath $image) {
    Assert-File $image $data.image
    Write-Host "ISO already verified: $image"
    return
}
[long]$missing = 0
foreach ($part in $data.parts) {
    $path = Join-Path $folder $part.name
    if (Test-Path -LiteralPath $path) {
        Assert-File $path $part
    } elseif ($Offline) {
        throw "Offline part is missing: $path"
    } else {
        $missing += $part.bytes
    }
}
$drive = New-Object IO.DriveInfo ([IO.Path]::GetPathRoot($folder))
if ($drive.AvailableFreeSpace -lt ($missing + $data.image.bytes)) {
    throw 'Insufficient space for missing parts and the assembled ISO.'
}
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
foreach ($part in $data.parts) { Save-Part $part $folder }
$temporary = Join-Path $folder ([guid]::NewGuid().ToString() + '.partial')
$destination = $null
try {
    Write-Host 'Assembling and verifying the ISO...'
    $destination = [IO.File]::Open($temporary, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
    foreach ($part in $data.parts) {
        $source = [IO.File]::OpenRead((Join-Path $folder $part.name))
        try { Copy-Bytes $source $destination $part.bytes } finally { $source.Dispose() }
    }
    $destination.Dispose()
    $destination = $null
    Assert-File $temporary $data.image
    # Two-argument File.Move never replaces an existing destination, even in a race.
    [IO.File]::Move($temporary, $image)
} finally {
    if ($null -ne $destination) { $destination.Dispose() }
    if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) }
}
Write-Host "ISO verified: $image"
Write-Host ('SHA-256: ' + $data.image.sha256)
