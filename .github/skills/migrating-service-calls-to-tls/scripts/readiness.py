"""Builds the consumer readiness report from the producer's access log.

usage: readiness.py --log <file> [--log <file> ...] --allowlist <allowed-consumers.yaml>
                    --out <readiness.json> [--md <consumer-readiness.md>]
                    [--min-observation-days N] [--signoff <cutover-signoff.yaml>]
                    [--signoff-roles "producer service owner,..."] [--now <ISO time>]
                    [--probe-tags <probe-tags.log>]

The producer writes one line per request (see references/producer.md):

    tls-migration access ts=2026-11-14T05:10:00Z scheme=https client_cert=yes cn=orders allowed=yes probe=- path=/stock/SKU-1

A line is read only when it is exactly that record: the marker starts the
message, either at the start of the line or right after the first " : " (the
separator in Spring Boot's default log pattern, after the logger name), and is
followed by the seven fields, once each, in that order, and nothing else
(scheme http|https, client_cert yes|no, allowed yes|no|n/a). Any other line that
holds the marker (an application message that quotes it, a field twice, a
missing probe= field, a ts= that is not a time) is rejected and counted in
rejected_lines; it never makes a consumer ready.

Lines with probe=<tag> claim to come from probe-tls.sh (header X-TLS-Migration-Probe).
Anyone can send that header, so a tag can only count against the migration:
  - a tag probe-tls.sh or check.sh --live itself recorded (probe-tags.log beside
    probes.json, a fresh random tag per run) is the gate's own probe: left out;
  - any other tagged line over plain HTTP is still a plain-HTTP call, over HTTPS
    without a certificate still a call without a certificate, and over mutual
    TLS it never shows that a consumer has moved.

Rules (design section 8.2):
  - A consumer is ready when it was seen on mutual TLS with its own CN, and let
    through (allowed=yes), inside its window: max(min observation days,
    cadence + 7 days). A call refused with allowed=no does not count.
  - The log must reach back over the whole window. A log that covers 2 days
    cannot show that a monthly consumer has moved: that consumer is not ready.
  - Plain-HTTP calls cannot be attributed to a consumer (they carry no
    certificate). Any plain-HTTP call inside the window blocks closing HTTP.
  - HTTPS calls without a client certificate inside the window block stage 5:
    those callers break when client-auth becomes need.
  - A sign-off by a named person in an allowed role can accept named unready
    consumers, plain-HTTP calls (accepted_http_calls: true) and calls without a
    certificate (accepted_certless_calls: true) as breaking. Only the YAML
    boolean true accepts; any other value but false ("false" in quotes, "no",
    1) makes the whole sign-off invalid.
  - The probe identities (ids starting tls-probe-) are on the allowlist for the
    gate's own probes; they are not consumers and get no readiness row. It is recorded,
    never assumed, and check.sh reports a run that relies on it as
    "pass with exceptions", because the file is written inside the session.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True  # never leave __pycache__ in the skill folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tlslib  # noqa: E402

MARKER = "tls-migration access "
# The whole record, anchored at the start of the message: every field once, in order, nothing after.
RECORD = re.compile(r"tls-migration access ts=(?P<ts>\S+) scheme=(?P<scheme>https?) client_cert=(?P<client_cert>yes|no)"
                    r" cn=(?P<cn>\S+) allowed=(?P<allowed>yes|no|n/a) probe=(?P<probe>\S+) path=(?P<path>\S+)[ \t]*")
PROBE_IDENTITY = "tls-probe-"
CADENCE_DAYS = {"continuous": 0, "hourly": 0, "daily": 1, "weekly": 7, "monthly": 31, "quarterly": 92}


def parse_record(raw: str) -> dict[str, str] | None:
    """The fields of an access record, or None when the line is not exactly one
    (see the header). The message starts at the line start or after the first " : "."""
    separator = raw.find(" : ")
    starts = [0] + ([separator + 3] if separator >= 0 else [])
    for start in starts:
        message = raw[start:].lstrip(" ") if start else raw
        match = RECORD.fullmatch(message)
        if match:
            return match.groupdict()
    return None


def read_probe_tags(path: str | None, out: str) -> set[str]:
    """Tags the probe scripts recorded for their own requests. Default: probe-tags.log
    in the --out folder (probes.json, probe-tags.log and readiness.json all live
    in tls-migration/evidence/)."""
    candidate = Path(path) if path else Path(out).parent / "probe-tags.log"
    if not candidate.is_file():
        return set()
    return {token for line in tlslib.read_regular(candidate, errors="replace").splitlines() for token in line.split()[1:]}


def read_events(paths: list[str], own_tags: set[str] | None = None,
                rejected: list[str] | None = None) -> list[dict[str, Any]]:
    """Access records from the logs. Lines that hold the marker but are not exactly a
    record are appended to `rejected` (as "file:line") and never read as one."""
    own_tags = own_tags or set()
    rejected = rejected if rejected is not None else []
    events = []
    for path in paths:
        for number, raw in enumerate(tlslib.read_regular(path, errors="replace").splitlines(), 1):
            if MARKER not in raw:
                continue
            fields = parse_record(raw)
            if fields is None:
                rejected.append(f"{path}:{number}")
                continue
            tag = fields.get("probe", "-")
            if tag != "-" and tag in own_tags:
                continue  # the gate's own probes, not consumer traffic
            fields["tagged"] = tag != "-"   # a tag nobody recorded: counts against, never for
            try:
                fields["when"] = tlslib._parse_iso(fields["ts"])  # noqa: SLF001
            except (KeyError, ValueError):
                rejected.append(f"{path}:{number}")
                continue
            events.append(fields)
    return events


def moved(event: dict[str, Any]) -> bool:
    """A call that shows its consumer has moved: mutual TLS, let through, not tagged."""
    return event.get("scheme") == "https" and event.get("client_cert") == "yes" and event.get("allowed") == "yes" \
        and not event["tagged"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log", action="append", required=True)
    parser.add_argument("--allowlist", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--md")
    parser.add_argument("--min-observation-days", type=int, default=14)
    parser.add_argument("--signoff")
    parser.add_argument("--signoff-roles", default="producer service owner")
    parser.add_argument("--now")
    parser.add_argument("--probe-tags", help="tags recorded by probe-tls.sh; default probe-tags.log in the --out folder")
    args = parser.parse_args()
    args.min_observation_days = max(0, args.min_observation_days)   # a negative window would look into the future

    now = tlslib._parse_iso(args.now) if args.now else tlslib.now_utc()  # noqa: SLF001
    allow = tlslib.load_yaml(args.allowlist) or {}
    # The probe identities (tls-probe-allowed, tls-probe-unlisted) are the gate's own
    # certificates on the allowlist, not consumers: they never need to be seen moving.
    consumers = [c for c in allow.get("consumers") or [] if isinstance(c, dict) and c.get("id")
                 and not str(c["id"]).startswith(PROBE_IDENTITY)]
    rejected: list[str] = []
    events = read_events(args.log, read_probe_tags(args.probe_tags, args.out), rejected)
    earliest = min((e["when"] for e in events), default=None)
    span_days = (now - earliest).total_seconds() / 86400 if earliest else 0.0

    signoff: dict[str, Any] = {}
    signoff_valid = False
    signoff_problems: list[str] = []
    if args.signoff and Path(args.signoff).exists():
        signoff = tlslib.load_yaml(args.signoff) or {}
        if not isinstance(signoff, dict):
            signoff, signoff_problems = {}, ["the sign-off is not a mapping"]
        roles = {r.strip().lower() for r in args.signoff_roles.split(",") if r.strip()}
        # A flag accepts only when it is the YAML boolean true. "false", "no" in
        # quotes, 1 or a list are not a yes, and a sign-off that says one of them
        # is not a sign-off anyone can rely on: it is refused as a whole.
        for flag in ("accepted_http_calls", "accepted_certless_calls"):
            if flag in signoff and signoff[flag] is not True and signoff[flag] is not False and signoff[flag] is not None:
                signoff_problems.append(f"{flag} is {signoff[flag]!r}; it must be true or false (unquoted)")
        unready_list = signoff.get("accepted_unready")
        if unready_list is not None and not (isinstance(unready_list, list) and all(isinstance(x, str) for x in unready_list)):
            signoff_problems.append("accepted_unready must be a list of consumer ids")
        signoff_valid = bool(
            not signoff_problems
            and str(signoff.get("signed_by") or "").strip()
            and str(signoff.get("role") or "").strip().lower() in roles
            and str(signoff.get("date") or "").strip()
        )
    accepted = {str(x) for x in (signoff.get("accepted_unready") or [])} if signoff_valid else set()

    rows = []
    for consumer in consumers:
        cid = str(consumer["id"])
        cadence = str(consumer.get("cadence") or "unknown")
        cadence_days = CADENCE_DAYS.get(cadence)
        window = max(args.min_observation_days, (cadence_days if cadence_days is not None else 31) + 7) \
            if args.min_observation_days > 0 else 0
        since = now - dt.timedelta(days=window) if window else None
        mine = [e for e in events if e.get("cn") == cid and (since is None or e["when"] >= since)]
        # Seen on mutual TLS AND let through: a call the producer refused (allowed=no, a CN the
        # running service does not allow) shows the consumer has not moved.
        mtls = [e for e in mine if moved(e)]
        last = max((e["when"] for e in mtls), default=None)
        if cadence_days is None:
            status, reason = "unready", f"cadence '{cadence}' unknown; declare continuous, daily, weekly or monthly"
        elif not mtls:
            status, reason = "unready", f"not seen on mutual TLS in the last {window} days" if window else "never seen on mutual TLS"
        elif window and span_days < window:
            status, reason = "unready", f"the log covers {span_days:.1f} days; the window is {window}"
        else:
            status, reason = "ready", "seen on mutual TLS with its own certificate"
        rows.append({
            "id": cid, "owner": consumer.get("owner"), "cadence": cadence, "window_days": window,
            "last_seen_mtls": tlslib.iso(last), "status": status, "reason": reason,
            "accepted_by_signoff": status != "ready" and cid in accepted,
        })

    # Plain-HTTP and certificate-less calls are looked for over the longest
    # consumer window: a monthly caller still on HTTP shows up once a month.
    window_all = max([args.min_observation_days] + [r["window_days"] for r in rows]) if args.min_observation_days else 0
    if window_all:
        since_all = now - dt.timedelta(days=window_all)
        window_text = f"in the last {window_all} days"
    else:
        # No observation window (local): count plain-HTTP calls made after the
        # last consumer was first seen on mutual TLS, i.e. after everyone moved.
        firsts = [min((e["when"] for e in events if e.get("cn") == r["id"] and moved(e)), default=None) for r in rows]
        since_all = max((f for f in firsts if f), default=None) if all(firsts) else None
        window_text = "after every consumer had moved" if since_all else "in the whole log"
    # The boundary is inclusive: a call in the same second as the cut-over counts.
    http_calls = [e for e in events if e.get("scheme") == "http" and (since_all is None or e["when"] >= since_all)]
    # Callers on HTTPS without a certificate break the moment client-auth becomes need.
    certless_calls = [e for e in events if e.get("scheme") == "https" and e.get("client_cert") != "yes"
                      and (since_all is None or e["when"] >= since_all)]
    unlisted = sorted({e.get("cn") for e in events if e.get("allowed") == "no" and e.get("cn") not in (None, "-")})
    unready = [r for r in rows if r["status"] != "ready"]
    result = {
        "tool": "readiness.py",
        "generated_at": tlslib.iso(now),
        "log_files": [tlslib.shown_path(item, tlslib.find_repo_root(args.out)) for item in args.log],
        "log_span_days": round(span_days, 2),
        "events": len(events),
        # Lines that hold the access marker but are not exactly one record: never read.
        "rejected_lines": len(rejected),
        "rejected_line_refs": rejected[:20],
        "min_observation_days": args.min_observation_days,
        "consumers": rows,
        "unready": [r["id"] for r in unready],
        "unready_without_signoff": sum(1 for r in unready if not r["accepted_by_signoff"]),
        "http_calls_in_window": len(http_calls),
        "http_calls_accepted_by_signoff": bool(signoff_valid and signoff.get("accepted_http_calls") is True),
        "https_calls_without_certificate_in_window": len(certless_calls),
        "certless_calls_accepted_by_signoff": bool(signoff_valid and signoff.get("accepted_certless_calls") is True),
        "unlisted_cns_seen": unlisted,
        # str(): YAML reads an unquoted date as a date object, which JSON cannot hold.
        "signoff": {"file": tlslib.shown_path(args.signoff, tlslib.find_repo_root(args.out)) if args.signoff else None,
                    "valid": signoff_valid, "problems": signoff_problems,
                    **({k: None if signoff.get(k) is None else str(signoff.get(k)) for k in ("signed_by", "role", "date")}
                       if signoff else {})},
    }
    result["ready_for_stage_5"] = result["unready_without_signoff"] == 0 and bool(rows) and (
        result["https_calls_without_certificate_in_window"] == 0 or result["certless_calls_accepted_by_signoff"]
    )
    result["ready_for_stage_6"] = result["ready_for_stage_5"] and (
        result["http_calls_in_window"] == 0 or result["http_calls_accepted_by_signoff"]
    )
    tlslib.write_json(args.out, result)   # no --repo here: the repository is found from --out

    lines = [
        "# Consumer readiness",
        "",
        f"Generated {result['generated_at']} from {len(events)} log lines covering {span_days:.1f} days.",
        "",
        "| consumer | cadence | window (days) | last seen on mTLS | status | reason |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        mark = "✅" if r["status"] == "ready" else ("⚠️ accepted by sign-off" if r["accepted_by_signoff"] else "❌")
        lines.append(f"| {r['id']} | {r['cadence']} | {r['window_days']} | {r['last_seen_mtls'] or '-'} | {mark} | {r['reason']} |")
    lines += [
        "",
        f"Plain-HTTP calls {window_text}: {len(http_calls)}",
        f"HTTPS calls without a client certificate {window_text}: {len(certless_calls)}",
        f"Certificates seen that are not on the allowlist: {', '.join(unlisted) or 'none'}",
        f"Lines with the access marker that are not an exact access record (rejected, never read): {len(rejected)}",
        f"Ready for stage 5 (require client certificates): {'yes' if result['ready_for_stage_5'] else 'no'}",
        f"Ready for stage 6 (close plain HTTP): {'yes' if result['ready_for_stage_6'] else 'no'}",
    ]
    if args.md:
        tlslib.write_text(args.md, "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except tlslib.UnsafeWrite as refused:   # a link or a path out of the repository (D2): nothing written
        print(f"refused: {refused}", file=sys.stderr)
        sys.exit(2)
