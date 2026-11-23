# Routes through a gateway

When calls pass through a routing gateway there are two connections, and each is planned on its own:

```
caller  --(1)-->  gateway  --(2)-->  receiver
```

| | Connection 1: caller to gateway | Connection 2: gateway to receiver |
| --- | --- | --- |
| Server certificate | The gateway's, for the name callers use | The receiver's, for the name the gateway uses |
| Who verifies it | The caller | The gateway |
| Client certificate (mutual) | The caller's, verified by the gateway | The gateway's, verified by the receiver |

For Apigee, also read [apigee.md](apigee.md).

## Questions to settle in step 1 (side and inputs)

1. Which product the gateway is, and who owns it.
2. Whether it ends TLS and opens a new connection (the usual case), or passes the encrypted connection through untouched. With pass-through there is one connection end to end and the gateway holds no certificate for it.
3. Whether its configuration is in a repository in scope.
4. Whether the receiver must know who the original caller was. When the gateway ends TLS, the receiver sees the gateway's certificate, not the caller's. If the receiver needs the caller's identity, the gateway must pass it on in a way the receiver can trust, and the receiver must accept it only from the gateway.
5. Whether anything can reach the receiver without going through the gateway. If so, connection 2 needs mutual TLS so the receiver accepts the gateway only.

## What the assistant does

- Adds both connections to the inventory diagram and the certificate plan.
- Changes the caller as in [consumer.md](consumer.md) and the receiver as in the producer stages ([producer.md](producer.md)). The receiver trusts the gateway's client certificate, not each caller's.
- Lists **the gateway** as the consumer in the receiver's `allowed-consumers.yaml`: every call arrives with the gateway's certificate, so the receiver's log and readiness report show one consumer, the gateway. Whether each original caller has moved is shown on connection 1, from the gateway's own log; say in the report that the receiver's readiness covers the gateway only.
- For the gateway itself, follows the policy file's `gateway_changes` (`prepare-request` when the policy does not set it):
  - `prepare-request`: writes `tls-migration/requests/gateway-change.md` with, per route: the listener and certificate for connection 1, the upstream address, scheme and trust for connection 2, the client certificate the gateway presents, client-certificate checking on connection 1, the minimum TLS version, and how to verify and roll back. It does not edit gateway configuration.
  - `agent-may-edit`: makes the same changes in the gateway's configuration files in the repository, as a separate change from the application changes.

## Order

1. Receiver accepts TLS beside plain HTTP.
2. Gateway upstream switches to HTTPS and verifies the receiver.
3. Gateway listener serves TLS; callers switch to the HTTPS address and verify the gateway.
4. Client certificates: caller to gateway, then gateway to receiver.
5. Plain HTTP is closed on the receiver and on the gateway listener.

Verify each connection separately with the probes in [verify-and-report.md](verify-and-report.md). A call that works end to end does not show that both connections are encrypted.
