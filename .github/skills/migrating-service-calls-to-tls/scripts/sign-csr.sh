#!/usr/bin/env bash
# Signs a consumer's certificate request with the producer's consumer CA
# (local and test only). Staging and production requests go to the company CA,
# Vault or cert-manager; this script refuses them.
#
# usage: sign-csr.sh --env local|test --producer <p> --csr <file> --allowlist <allowed-consumers.yaml> --out <dir> [--days N] [--name <file name>]
#
# The request is treated as untrusted: the CN must be in the allowlist, the
# allowlist must be this producer's own ("producer: <p>"), and every extension
# the request asks for is dropped and replaced (client-only, CA:FALSE).
# Every tls-probe-* CN is refused: make-probe-certs.sh issues those.
# Writes <out>/<producer>-<consumer>.crt, or <out>/<name> with --name. Use one
# --out folder per consumer (tls-migration/signed/<consumer>) and --name
# client.crt for a first certificate, --name client.crt.next for a renewal:
# the consumer saves it under that name and swaps it in with
# make-csr.sh --activate. The lifetime never runs past the CA's end.
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
require_openssl3
exec python3 -I -B "$scripts_dir/sign_csr.py" "$@"
