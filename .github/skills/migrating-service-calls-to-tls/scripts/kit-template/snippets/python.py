# Python with requests: calling {{PRODUCER}} with your client certificate.
import requests

response = requests.get(
    "{{ENDPOINT}}",
    cert=("/etc/tls/{{PRODUCER}}/client.crt", "/etc/tls/{{PRODUCER}}/client.key"),
    verify="/etc/tls/{{PRODUCER}}/ca-bundle.pem",  # a path, never False
    timeout=10,
)
response.raise_for_status()
print(response.status_code)
