#!/usr/bin/env bash
# curl: calling {{PRODUCER}} with your client certificate. Never add -k.
# Run it from anywhere; it reads the kit folder it sits in.
cd "$(dirname "${BASH_SOURCE[0]}")/.."
curl --fail --show-error \
  --cacert ca-bundle.pem \
  --cert client.crt \
  --key "${TLS_PRIVATE_DIR:-$HOME/.tls-migration/private}/{{KEY_SUBPATH}}/client.key" \
  "{{ENDPOINT}}"
