# Pester 5 tests for make-csr.ps1. Run where pwsh and Pester exist:
#   pwsh -NoProfile -Command Invoke-Pester -Path make-csr.Tests.ps1 -CI
# (-CI exits non-zero when a test fails.) Needs OpenSSL 3 or later on the PATH.
# testbench/test_certs.py runs this file when pwsh is on the PATH (else it reports "skipped": no pwsh, or no Pester 5 or later).
#
# Every test runs make-csr.ps1 in a fresh pwsh, from a copy in a fake kit
# folder whose endpoint.txt has Windows (CRLF) line ends, with
# TLS_PRIVATE_DIR pointed at a temporary folder.

BeforeAll {
    $script:pwshPath = (Get-Process -Id $PID).Path
    $script:kit = Join-Path $TestDrive "kit"
    $script:private = Join-Path $TestDrive "private"
    $script:requests = Join-Path $TestDrive "requests"
    New-Item -ItemType Directory -Force -Path $script:kit | Out-Null
    Copy-Item (Join-Path $PSScriptRoot "make-csr.ps1") $script:kit
    # CRLF line ends and a trailing space: the script must trim both.
    [System.IO.File]::WriteAllText((Join-Path $script:kit "endpoint.txt"),
        "url=https://inventory:8443/stock`r`nconsumer=orders`r`nproducer=inventory `r`nenvironment=test`r`n")
    $env:TLS_PRIVATE_DIR = $script:private
    $env:NO_COLOR = "1"
    $script:keyDir = Join-Path (Join-Path (Join-Path $script:private "test") "inventory") "orders"
    $script:key = Join-Path $script:keyDir "client.key"

    $banner = (& openssl version) | Select-Object -First 1
    if ($LASTEXITCODE -ne 0 -or $banner -notmatch '^OpenSSL [3-9]') { throw "these tests need OpenSSL 3 or later on the PATH (found '$banner')" }

    function script:Invoke-MakeCsr([string[]]$Arguments) {
        $output = & $script:pwshPath -NoProfile -NonInteractive -File (Join-Path $script:kit "make-csr.ps1") @Arguments 2>&1
        # One line, single spaces: an error message wrapped at the console width still matches.
        $text = (($output | ForEach-Object { "$_" }) -join " ") -replace '\s+', ' '
        return [pscustomobject]@{ Code = $LASTEXITCODE; Text = $text }
    }
    function script:Invoke-Ssl([string[]]$Arguments) {
        $output = & openssl @Arguments
        if ($LASTEXITCODE -ne 0) { throw "openssl $($Arguments -join ' ') failed" }
        return $output
    }
    # A certificate for the public key of $KeyFile, signed by that key itself:
    # enough for make-csr.ps1, which compares public keys and the CN only.
    function script:New-TestCert([string]$KeyFile, [string]$Cn, [string]$Path) {
        Invoke-Ssl @("req", "-new", "-x509", "-key", $KeyFile, "-subj", "/CN=$Cn", "-days", "1", "-out", $Path) | Out-Null
    }
    function script:Get-Sha([string]$Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash }
}

AfterAll {
    Remove-Item Env:TLS_PRIVATE_DIR, Env:NO_COLOR -ErrorAction SilentlyContinue
}

Describe "make-csr.ps1" {
    It "writes the request for the consumer from endpoint.txt and prints its subject and public key hash" {
        $run = Invoke-MakeCsr @("-Out", $script:requests)
        $run.Code | Should -Be 0 -Because $run.Text
        $csr = Join-Path $script:requests "inventory-orders.csr"
        $csr | Should -Exist
        $script:key | Should -Exist
        $run.Text | Should -Match "subject: CN=orders"
        $pem = Join-Path $TestDrive "request-pub.pem"
        $der = Join-Path $TestDrive "request-pub.der"
        Invoke-Ssl @("req", "-in", $csr, "-noout", "-pubkey", "-out", $pem) | Out-Null
        Invoke-Ssl @("pkey", "-pubin", "-in", $pem, "-outform", "DER", "-out", $der) | Out-Null
        $expected = (Get-Sha $der).ToLowerInvariant()
        $run.Text | Should -Match "public key sha256: $expected"
        (Invoke-Ssl @("req", "-in", $csr, "-noout", "-subject")) -join "" | Should -Match "CN\s*=\s*orders$"
    }

    It "refuses a positional argument" {
        $run = Invoke-MakeCsr @("orders")
        $run.Code | Should -Not -Be 0
        $run.Text | Should -Match "positional parameter"
    }

    It "refuses an unknown -Env and makes no folder for it" {
        $run = Invoke-MakeCsr @("-Env", "prod", "-Out", $script:requests)
        $run.Code | Should -Not -Be 0
        $run.Text | Should -Match "prod"
        Join-Path $script:private "prod" | Should -Not -Exist
    }

    It "refuses -Activate with a certificate for another CN and changes nothing" {
        $renew = Invoke-MakeCsr @("-Renew", "-Out", $script:requests)
        $renew.Code | Should -Be 0 -Because $renew.Text
        $next = "$($script:key).next"
        $next | Should -Exist
        $other = Join-Path $TestDrive "other-cn.crt"
        New-TestCert $next "billing" $other
        $before = @{ key = Get-Sha $script:key; next = Get-Sha $next }
        $run = Invoke-MakeCsr @("-Activate", "-Cert", $other)
        $run.Code | Should -Not -Be 0
        $run.Text | Should -Match "is for CN=billing, not for orders; nothing was changed"
        Get-Sha $script:key | Should -Be $before.key
        Get-Sha $next | Should -Be $before.next
        Join-Path $script:kit "client.crt" | Should -Not -Exist
    }

    It "refuses -Activate with a certificate for the key already in use and changes nothing" {
        $next = "$($script:key).next"
        $inUse = Join-Path $TestDrive "in-use.crt"
        New-TestCert $script:key "orders" $inUse
        $before = @{ key = Get-Sha $script:key; next = Get-Sha $next }
        $run = Invoke-MakeCsr @("-Activate", "-Cert", $inUse)
        $run.Code | Should -Not -Be 0
        $run.Text | Should -Match "belongs to the key already in use, not to the renewal key; nothing was changed"
        Get-Sha $script:key | Should -Be $before.key
        Get-Sha $next | Should -Be $before.next
        Join-Path $script:kit "client.crt" | Should -Not -Exist
    }

    It "activates into a -CertOut folder that does not exist yet" {
        $next = "$($script:key).next"
        $renewed = Join-Path $TestDrive "client.crt.next"
        New-TestCert $next "orders" $renewed
        $nextSha = Get-Sha $next
        $target = Join-Path (Join-Path (Join-Path $TestDrive "deploy") "nested") "client.crt"
        $run = Invoke-MakeCsr @("-Activate", "-Cert", $renewed, "-CertOut", $target)
        $run.Code | Should -Be 0 -Because $run.Text
        $target | Should -Exist
        Get-Sha $target | Should -Be (Get-Sha $renewed)
        Get-Sha $script:key | Should -Be $nextSha
        $next | Should -Not -Exist
        "$($script:key).previous" | Should -Exist
    }

    Context "kit fingerprint" {
        BeforeAll {
            # A separate kit copy with its own SHA256SUMS, as build-consumer-kit.sh writes it.
            $script:fkit = Join-Path $TestDrive "fkit"
            New-Item -ItemType Directory -Force -Path $script:fkit | Out-Null
            Copy-Item (Join-Path $script:kit "make-csr.ps1") $script:fkit
            Copy-Item (Join-Path $script:kit "endpoint.txt") $script:fkit
            $lines = foreach ($name in @("endpoint.txt", "make-csr.ps1")) {
                "{0}  {1}" -f (Get-FileHash -LiteralPath (Join-Path $script:fkit $name) -Algorithm SHA256).Hash.ToLowerInvariant(), $name
            }
            [System.IO.File]::WriteAllText((Join-Path $script:fkit "SHA256SUMS"), (($lines -join "`n") + "`n"))
            $script:fprint = (Get-FileHash -LiteralPath (Join-Path $script:fkit "SHA256SUMS") -Algorithm SHA256).Hash.ToLowerInvariant()
            $script:fprivate = Join-Path $TestDrive "fprivate"
            function script:Invoke-KitCsr([string[]]$Arguments) {
                $saved = $env:TLS_PRIVATE_DIR
                $env:TLS_PRIVATE_DIR = $script:fprivate
                try {
                    $output = & $script:pwshPath -NoProfile -NonInteractive -File (Join-Path $script:fkit "make-csr.ps1") @Arguments 2>&1
                    $code = $LASTEXITCODE
                } finally { $env:TLS_PRIVATE_DIR = $saved }
                return [pscustomobject]@{ Code = $code; Text = ((($output | ForEach-Object { "$_" }) -join " ") -replace '\s+', ' ') }
            }
        }

        It "refuses a wrong fingerprint before any key is made" {
            $run = Invoke-KitCsr @("-KitFingerprint", ("0" * 64), "-Out", (Join-Path $TestDrive "fout1"))
            $run.Code | Should -Not -Be 0
            $run.Text | Should -Match "the kit fingerprint does not match"
            $script:fprivate | Should -Not -Exist
        }

        It "refuses a kit file changed after SHA256SUMS was written" {
            $copy = Join-Path $TestDrive "endpoint.bak"
            Copy-Item (Join-Path $script:fkit "endpoint.txt") $copy
            Add-Content -LiteralPath (Join-Path $script:fkit "endpoint.txt") -Value "producer=evil"
            try {
                $run = Invoke-KitCsr @("-KitFingerprint", $script:fprint, "-Out", (Join-Path $TestDrive "fout2"))
            } finally { Copy-Item $copy (Join-Path $script:fkit "endpoint.txt") -Force }
            $run.Code | Should -Not -Be 0
            $run.Text | Should -Match "endpoint.txt does not match SHA256SUMS"
            $script:fprivate | Should -Not -Exist
        }

        It "goes on with the right fingerprint" {
            $run = Invoke-KitCsr @("-KitFingerprint", $script:fprint.ToUpperInvariant(), "-Out", (Join-Path $TestDrive "fout3"))
            $run.Code | Should -Be 0 -Because $run.Text
            $run.Text | Should -Match "kit checked"
            Join-Path (Join-Path (Join-Path (Join-Path $script:fprivate "test") "inventory") "orders") "client.key" | Should -Exist
        }
    }
}
