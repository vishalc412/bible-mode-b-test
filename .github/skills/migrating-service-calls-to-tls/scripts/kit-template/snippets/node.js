// Node 18+: calling {{PRODUCER}} with your client certificate.
const fs = require("node:fs");
const https = require("node:https");

const agent = new https.Agent({
  cert: fs.readFileSync("/etc/tls/{{PRODUCER}}/client.crt"),
  key: fs.readFileSync("/etc/tls/{{PRODUCER}}/client.key"),
  ca: fs.readFileSync("/etc/tls/{{PRODUCER}}/ca-bundle.pem"), // replaces the default CAs for this agent
  minVersion: "TLSv1.2",
  // rejectUnauthorized stays at its default (true). Never set it to false.
});

https.get("{{ENDPOINT}}", { agent }, (res) => {
  console.log(res.statusCode);
  res.resume();
});
