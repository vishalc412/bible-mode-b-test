# Makes this consumer's private key and certificate request on Windows.
# Needs OpenSSL 3 on the PATH (Git for Windows ships one). The toolkit's tests
# run make-csr.Tests.ps1 (Pester) only on a machine that has pwsh; elsewhere
# this file is checked by reading only. Read it before you rely on it, or use
# make-csr.sh from a bash shell (Git Bash), which is always tested.
#
# usage: .\make-csr.ps1 [-Consumer <id>] [-Producer <name>] [-Env <env>] [-Out <folder>]
#                       [-Renew [-Force] | -Activate -Cert <new certificate> [-CertOut <file>] | -Replace]
#                       [-KitFingerprint <sha256>]
#
#   Every value is given by name; nothing is taken by position.
#   In a kit, -Consumer, -Producer and -Env come from endpoint.txt: run .\make-csr.ps1 with no arguments.
#   -Renew     a new key in client.key.next and a request from it; the key in use stays.
#              Refused while an earlier renewal is waiting (-Force starts again).
#   -Activate -Cert <file>
#              (save a renewal as client.crt.next, never over client.crt, which is in use)
#              checks that the new certificate is for this consumer and belongs to
#              client.key.next, then swaps key and certificate together (the old pair
#              is kept as *.previous). -CertOut is the certificate file your service
#              reads; its folder is made if missing.
#              Then restart the service or update its secret.
#   -Replace   a new client.key straight away (a lost key). The certificate in use stops matching.
#   -KitFingerprint  the kit fingerprint (the SHA-256 of SHA256SUMS) the producer team sent apart
#              from the kit. Checked, with every file SHA256SUMS lists, before anything else.
#   For staging and production it asks for the environment's name to be typed
#   first, and stops when its input is redirected: a person runs it.
#
# The key goes to <root>\[<env>\]<producer>\<consumer>\client.key, readable by
# you only. <root> is $env:TLS_PRIVATE_DIR, default $HOME\.tls-migration\private.
# Send only the .csr to the producer team.
[CmdletBinding(PositionalBinding = $false)]
param(
    [ValidatePattern('^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$', Options = 'None')][string]$Consumer,
    [ValidatePattern('^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$', Options = 'None')][string]$Producer,
    [Alias("Env")][ValidateSet("local", "test", "staging", "production", IgnoreCase = $false)][string]$Environment,
    [string]$Out = ".",
    [switch]$Renew,
    [switch]$Force,
    [switch]$Activate,
    [string]$Cert,
    [string]$CertOut,
    [switch]$Replace,
    [string]$KitFingerprint
)
$ErrorActionPreference = "Stop"
# One plain line per error, the same on every console width and PowerShell version.
trap { [Console]::Error.WriteLine("error: " + $_.Exception.Message); exit 1 }
$idPattern = '^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'

# The kit, checked against the fingerprint sent apart from it, before endpoint.txt or any key is read.
if ($KitFingerprint) {
    $wanted = ($KitFingerprint -replace '[:\s]', '').ToLowerInvariant()
    if ($wanted -notmatch '^[0-9a-f]{64}$') { throw "-KitFingerprint must be a SHA-256: 64 hexadecimal characters" }
    $sums = Join-Path $PSScriptRoot "SHA256SUMS"
    if (-not (Test-Path -LiteralPath $sums -PathType Leaf) -or (Get-Item -LiteralPath $sums).LinkType) { throw "this kit has no SHA256SUMS, so it cannot be checked; do not use it, call the producer team. Nothing was done." }
    if ((Get-FileHash -LiteralPath $sums -Algorithm SHA256).Hash.ToLowerInvariant() -ne $wanted) { throw "the kit fingerprint does not match: SHA256SUMS is not the one the producer team sent. Do not use this kit; call the producer team. Nothing was done." }
    foreach ($entry in Get-Content -LiteralPath $sums) {
        if ($entry -cnotmatch '^([0-9a-f]{64})  (.+)$') { throw "SHA256SUMS holds a line that is not '<sha256>  <file>'; do not use this kit. Nothing was done." }
        $listedHash = $Matches[1]; $listedName = $Matches[2]
        if ("/$listedName/" -match '/\.\./' -or $listedName.StartsWith('/') -or $listedName -match '\\') { throw "SHA256SUMS names $listedName, outside the kit; do not use this kit. Nothing was done." }
        $listedPath = Join-Path $PSScriptRoot $listedName
        if (-not (Test-Path -LiteralPath $listedPath -PathType Leaf) -or (Get-Item -LiteralPath $listedPath).LinkType) { throw "$listedName, listed in SHA256SUMS, is missing from the kit; do not use it. Nothing was done." }
        if ((Get-FileHash -LiteralPath $listedPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $listedHash) { throw "$listedName does not match SHA256SUMS: the kit was changed. Do not use it; call the producer team. Nothing was done." }
    }
    [Console]::Error.WriteLine("kit checked: SHA256SUMS matches the fingerprint and every file it lists matches")
}

$inKit = $false
$endpointFile = Join-Path $PSScriptRoot "endpoint.txt"
if (Test-Path $endpointFile) {
    $inKit = $true
    foreach ($line in Get-Content $endpointFile) {
        # Trimmed, so a trailing space or a CR from a file saved on Windows is not part of the value.
        $line = $line.Trim()
        if (-not $Consumer -and $line -like "consumer=*" -and $line.Substring(9).Trim()) { $Consumer = $line.Substring(9).Trim() }
        if (-not $Producer -and $line -like "producer=*" -and $line.Substring(9).Trim()) { $Producer = $line.Substring(9).Trim() }
        if (-not $Environment -and $line -like "environment=*" -and $line.Substring(12).Trim()) { $Environment = $line.Substring(12).Trim() }
    }
}
if (-not $Consumer) { throw "-Consumer <id> is required (in a kit it comes from endpoint.txt)" }
if (-not $Producer) { throw "-Producer <name> is required: every producer gets its own key" }
if ($Consumer -cnotmatch $idPattern) { throw "consumer id must be lowercase letters, digits and hyphens" }
if ($Producer -cnotmatch $idPattern) { throw "producer name must be lowercase letters, digits and hyphens" }
if ($Environment -and @("local", "test", "staging", "production") -cnotcontains $Environment) { throw "unknown environment '$Environment'" }
$modes = 0
if ($Renew) { $modes++ }
if ($Activate) { $modes++ }
if ($Replace) { $modes++ }
if ($modes -gt 1) { throw "use one of -Renew, -Activate, -Replace" }

# Every openssl call goes through here, so none can fail unnoticed.
function Invoke-OpenSsl {
    param([string]$What, [string[]]$Arguments)
    $output = & openssl @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$What failed (openssl exit $LASTEXITCODE)" }
    return $output
}

# "openssl 3" means OpenSSL 3, not LibreSSL 3.
if (-not (Get-Command openssl -ErrorAction SilentlyContinue)) { throw "OpenSSL 3 or later is needed and was not found on the PATH. Ask the person at this machine to install it; an assistant never installs software or changes the machine." }
$banner = (Invoke-OpenSsl "reading the OpenSSL version" @("version")) | Select-Object -First 1
$major = 0
if ($banner -match '^OpenSSL (\d+)\.') { $major = [int]$Matches[1] }
if ($major -lt 3) { throw "OpenSSL 3 or later is needed (found '$banner'). Ask the person at this machine to install it; an assistant never installs software or changes the machine." }

function New-Key([string]$Path) {
    # A named curve, never explicit parameters: Java, Go and most TLS stacks refuse those.
    Invoke-OpenSsl "making the key" @("genpkey", "-algorithm", "EC", "-pkeyopt", "ec_paramgen_curve:P-256", "-pkeyopt", "ec_param_enc:named_curve", "-out", $Path) | Out-Null
}
# The public half only, as text, to compare a key with a certificate.
function Get-PublicOfKey([string]$Path) { return ((Invoke-OpenSsl "reading the key's public half" @("pkey", "-in", $Path, "-pubout")) -join "`n").Trim() }
function Get-PublicOfCert([string]$Path) { return ((Invoke-OpenSsl "reading the certificate" @("x509", "-in", $Path, "-noout", "-pubkey")) -join "`n").Trim() }
function Get-CertCn([string]$Path) {
    $subject = ((Invoke-OpenSsl "reading the certificate's subject" @("x509", "-in", $Path, "-noout", "-subject", "-nameopt", "RFC2253")) -join "").Trim()
    if ($subject -match '(^subject=|,)CN=([^,]+)') { return $Matches[2] }
    return ""
}
# SHA-256 of the DER public key in a request, as make-csr.sh prints it.
function Get-RequestPublicKeySha256([string]$Path) {
    $pem = [System.IO.Path]::GetTempFileName()
    $der = [System.IO.Path]::GetTempFileName()
    try {
        Invoke-OpenSsl "reading the request's public key" @("req", "-in", $Path, "-noout", "-pubkey", "-out", $pem) | Out-Null
        Invoke-OpenSsl "converting the public key" @("pkey", "-pubin", "-in", $pem, "-outform", "DER", "-out", $der) | Out-Null
        return (Get-FileHash -LiteralPath $der -Algorithm SHA256).Hash.ToLowerInvariant()
    } finally {
        Remove-Item -LiteralPath $pem, $der -Force -ErrorAction SilentlyContinue
    }
}
# The real path of an existing folder: full, with symbolic links and junctions
# followed where this PowerShell can (ResolveLinkTarget needs PowerShell 7.2+;
# Windows PowerShell 5.1 keeps the full path as it is).
function Resolve-RealPath([string]$Path) {
    $full = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Path).ProviderPath)
    $parent = Split-Path $full -Parent
    if ($parent -and $parent -ne $full -and (Test-Path -LiteralPath $parent)) { $full = Join-Path (Resolve-RealPath $parent) (Split-Path $full -Leaf) }
    $item = Get-Item -LiteralPath $full -Force
    if ($item.LinkType -and ($item.PSObject.Methods.Name -contains "ResolveLinkTarget")) {
        $target = $item.ResolveLinkTarget($true)
        if ($target) { $full = Resolve-RealPath $target.FullName }
    }
    return $full
}

# A staging or production key is made only by a person at a terminal, who types
# the environment's name when asked; redirected input is refused, so an
# assistant or an unattended job never gets past this. Nothing is made before.
if (-not $Activate -and @("staging", "production") -ccontains $Environment) {
    if ([Console]::IsInputRedirected) { throw "a $Environment key is made only by a person at a terminal: input is redirected, so nothing was made. An assistant never runs this for $Environment; it writes the command for the owners of the target." }
    $answer = Read-Host "This makes the client key and request of $Consumer for $Producer in $Environment. Type the environment name ($Environment) to go on, anything else stops"
    if ($answer -cne $Environment) { throw "not confirmed ('$Environment' was not typed); nothing was made" }
}

$privateRoot = if ($env:TLS_PRIVATE_DIR) { $env:TLS_PRIVATE_DIR } else { Join-Path $HOME ".tls-migration\private" }
$keyDir = $privateRoot
if ($Environment) { $keyDir = Join-Path $keyDir $Environment }
$keyDir = Join-Path (Join-Path $keyDir $Producer) $Consumer

# Refuse a key folder inside a repository, before creating anything. Checked
# on the real path of the nearest folder that exists, so a link cannot hide it.
$probe = $keyDir
while ($probe -and -not (Test-Path $probe)) { $probe = Split-Path $probe -Parent }
if ($probe) { $probe = Resolve-RealPath $probe }
while ($probe) {
    foreach ($marker in @(".git", ".svn", ".hg", "tls-migration")) {
        if (Test-Path (Join-Path $probe $marker)) { throw "$keyDir is inside a repository ($probe has $marker); set TLS_PRIVATE_DIR outside it" }
    }
    $parent = Split-Path $probe -Parent
    if (-not $parent -or $parent -eq $probe) { break }
    $probe = $parent
}
New-Item -ItemType Directory -Force -Path $keyDir | Out-Null

# Owner-only access on the key folder, set before any key is written; files
# made in it inherit it. By SID, not by user name, so a renamed account or a
# name that exists in two domains cannot point it at someone else.
# $IsWindows does not exist in Windows PowerShell 5.1 (the Desktop edition), which runs on Windows only.
$onWindows = ($PSVersionTable.PSEdition -eq "Desktop") -or $IsWindows
if ($onWindows) {
    $sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
    $acl = Get-Acl -LiteralPath $keyDir
    $acl.SetAccessRuleProtection($true, $false)
    foreach ($existing in @($acl.Access)) { [void]$acl.RemoveAccessRuleSpecific($existing) }
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule($sid, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
    $acl.AddAccessRule($rule)
    Set-Acl -LiteralPath $keyDir -AclObject $acl
} else {
    # Not Windows: there are no ACLs to set here. Mode 700 where .NET can set it
    # (PowerShell 7.3+); otherwise use make-csr.sh on this machine.
    $unixFileMode = "System.IO.UnixFileMode" -as [type]
    if ($unixFileMode) { [System.IO.File]::SetUnixFileMode($keyDir, [Enum]::Parse($unixFileMode, "UserRead, UserWrite, UserExecute")) }
}

$key = Join-Path $keyDir "client.key"
$next = "$key.next"
$previous = "$key.previous"

if ($Activate) {
    if (-not $Cert) { throw "-Activate needs -Cert <the new certificate>: the key is swapped only together with the certificate that belongs to it" }
    if (-not (Test-Path $Cert)) { throw "no certificate at $Cert" }
    if (-not (Test-Path $next)) { throw "no renewal key at $next; run with -Renew first" }
    $certPublic = Get-PublicOfCert $Cert
    if ($certPublic -ne (Get-PublicOfKey $next)) {
        if ((Test-Path $key) -and ($certPublic -eq (Get-PublicOfKey $key))) {
            throw "$Cert belongs to the key already in use, not to the renewal key; nothing was changed"
        }
        throw "$Cert does not belong to the renewal key in $next; nothing was changed. Send the request from the last -Renew, or run -Renew -Force and send that one."
    }
    $certCn = Get-CertCn $Cert
    if ($certCn -cne $Consumer) { throw "$Cert is for CN=$certCn, not for $Consumer; nothing was changed" }
    if (-not $CertOut) { $CertOut = if ($inKit) { Join-Path $PSScriptRoot "client.crt" } else { Join-Path $keyDir "client.crt" } }
    $certOutFolder = Split-Path $CertOut -Parent
    if ($certOutFolder) { New-Item -ItemType Directory -Force -Path $certOutFolder | Out-Null }
    # The new certificate saved over the one in use: the old one is lost and cannot be kept. Refused, with the way out.
    if ((Test-Path $CertOut) -and ((Resolve-Path $Cert).Path -eq (Resolve-Path $CertOut).Path)) {
        throw "$Cert is the certificate file your service reads: the new certificate was saved over the one in use, so the old certificate cannot be kept as .previous. Nothing was changed. Rename it to client.crt.next and run .\make-csr.ps1 -Activate -Cert client.crt.next. Save a renewal as client.crt.next next time."
    }
    Copy-Item $Cert "$CertOut.new" -Force
    $keptCert = $null
    if (Test-Path $CertOut) {
        if ((Get-FileHash $CertOut).Hash -ne (Get-FileHash $Cert).Hash) { Move-Item $CertOut "$CertOut.previous" -Force; $keptCert = "$CertOut.previous" }
    }
    $keptKey = $null
    if (Test-Path $key) { Move-Item $key $previous -Force; $keptKey = $previous }
    Move-Item $next $key -Force
    Move-Item "$CertOut.new" $CertOut -Force
    Write-Host "renewed: key $key and certificate $CertOut now belong together"
    if ($keptKey) { Write-Host "the old key is kept as $keptKey" }
    if ($keptCert) { Write-Host "the old certificate is kept as $keptCert" } else { Write-Host "no earlier certificate was kept (there was none, or it already held the new one)" }
    Write-Host "now restart the service, or update its secret from the new pair"
    exit 0
}

$signingKey = $key
if ($Renew) {
    if ((Test-Path $next) -and -not $Force) { throw "a renewal is already waiting for its certificate ($next exists). Activate it with -Activate -Cert <file>, or start again with -Renew -Force." }
    if (-not (Test-Path $key)) { throw "no key in use at $key; run without -Renew for a first request" }
    New-Key $next
    $signingKey = $next
} elseif ($Replace) {
    if (Test-Path $key) {
        Move-Item $key $previous -Force
        Write-Host "the key in use was replaced (kept as client.key.previous); the certificate in use no longer matches until the new one arrives"
    }
    New-Key $key
} elseif (Test-Path $key) {
    Write-Host "a key already exists for $Consumer at $Producer; re-using it (-Renew for a renewal, -Replace for a new key now)"
} else {
    New-Key $key
}

New-Item -ItemType Directory -Force -Path $Out | Out-Null
$csr = Join-Path $Out "$Producer-$Consumer.csr"
Invoke-OpenSsl "writing the request" @("req", "-new", "-key", $signingKey, "-subj", "/CN=$Consumer", "-out", $csr) | Out-Null
Write-Host "request: $csr  (send this file to the $Producer team)"
Write-Host "subject: CN=$Consumer"
Write-Host "public key sha256: $(Get-RequestPublicKeySha256 $csr)"
Write-Host "key kept at: $signingKey  (never send it, never commit it)"
if ($Renew) { Write-Host "when the new certificate arrives, save it as client.crt.next (not over client.crt, which is in use), then: .\make-csr.ps1 -Activate -Cert client.crt.next" }
