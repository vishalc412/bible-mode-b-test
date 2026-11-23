"""Repository scans shared by tls-inventory.sh and check.sh.

Plain text matching with fixed rules, so two runs over the same tree always
give the same answer. Nothing here can tell what the code does at run time:
the rules below are best-effort pattern matching, and the judge in
verifying-a-tls-migration owns the question "is checking really on".

Two kinds of hit:
  fail    the pattern in code or configuration
  review  the same pattern in documentation or inside a comment: listed for a
          person, never a failure on its own

Nothing is skipped silently. Every file or folder a scan did not read is
recorded with the reason (see SKIPPED); check.sh prints the list and turns
the ones that could hide a verdict (a link leaving the repository, a file it
could not read) into "not proven".
"""
from __future__ import annotations

import base64
import binascii
import bisect
import bz2
import fnmatch
import io
import lzma
import os
import re
import shutil
import stat
import sys
import tarfile
import tempfile
import zipfile
import zlib
from pathlib import Path
from typing import Any, Iterator

sys.dont_write_bytecode = True  # never leave __pycache__ in the skill folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tlslib  # noqa: E402

# Dependency caches, editor state and the installer's backups (an old copy of
# this skill quotes every pattern below): not scanned for code, and listed.
# The key scan (E4) reads them all the same; only .git is left out there.
SKIP_ALWAYS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".tox", ".pytest_cache",
    ".gradle", ".m2", ".npm", ".yarn", ".cache", ".idea", ".vscode", ".migration-toolkit-backups",
}
# vendor/ is a dependency folder only beside the file that fills it; a Java
# package called "vendor" is code.
VENDOR_MARKERS = {"go.mod", "composer.json", "Gemfile"}
# Build output, skipped only when it sits beside a build file AND holds compiled
# files: a bin/ or build/ folder of hand-written scripts is scanned.
BUILD_OUTPUT = {"target", "build", "dist", "out", "bin", "obj"}
BUILD_FILES = {"pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts",
               "package.json", "go.mod", "Cargo.toml", "build.sbt", "pyproject.toml"}
COMPILED = (".class", ".jar", ".war", ".o", ".obj", ".pyc", ".dll", ".exe", ".so", ".dylib", ".map", ".a", ".lib")
# Installed skills quote the patterns; matched at any depth.
SKILL_DIR = re.compile(r"(^|/)\.(claude|github|agents|cursor|copilot|codex|windsurf|gemini)/skills(/|$)")
MAX_BYTES = 64_000_000          # larger text files are listed, and still searched for key markers

# The skill's own working folder. Its reports and evidence quote URLs and
# patterns on purpose; only those file kinds are left out. Anything else the
# migration puts there (overrides, scripts, manifests) is scanned.
WORKING_DIR = "tls-migration"
WORKING_SKIP = re.compile(r"^tls-migration/(evidence|verification)/.*\.(json|log|md|txt)$"
                          r"|^tls-migration/[^/]+\.(md|ya?ml|json|txt)$"
                          r"|^tls-migration/local/(certs-to-check\.yaml|ca-fingerprints\.txt|probe-plan[^/]*\.ya?ml)$")
DOC_FILE = re.compile(r"\.(md|markdown|adoc|asciidoc|rst|txt)$", re.I)

KEY_FILE_GLOBS = ("*.key", "*.p12", "*.pfx", "*.pkcs12", "*.jks", "*.jceks", "*.bks", "*.keystore",
                  "*.p8", "*.pk8", "id_rsa", "id_ecdsa", "id_ed25519", "id_dsa")
STORE_PASSWORDS = ("", "changeit", "password", "secret")
# A key block: the marker, then a base64 body on the next line (a real line
# break or an escaped one). The marker alone, quoted in notes, is not a key.
PRIVATE_KEY_BLOCK = re.compile(
    r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----[ \t]*(?:\r?\n|\\r\\n|\\n)[ \t]*"
    r"(?:[A-Za-z-]+: [^\n]{0,200}(?:\r?\n|\\n)[ \t]*){0,4}(?:\r?\n|\\n)?[ \t]*[A-Za-z0-9+/=]{8,}")
KEY_MARKER = re.compile(rb"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----")
CERT_MARKER = re.compile(rb"-----BEGIN (?:X509 |TRUSTED )?CERTIFICATE-----")
BASE64_TOKEN = re.compile(r"[A-Za-z0-9+/]{20,}={0,2}$")
BASE64_LINE = re.compile(r"^[A-Za-z0-9+/]{2,}={0,2}$")
BASE64_RUN = re.compile(r"[A-Za-z0-9+/]{20,}={0,2}")

HOST_CHARS = r"[A-Za-z0-9_.\-]+"
# A host written as a placeholder the text does not resolve: ${X}, $(X), $X,
# {{ x }}, %s, {x}.
HOST_TEMPLATE = r"\$\{[^}\s]{1,120}\}|\$\([^)\s]{1,120}\)|\$[A-Za-z_]\w*|\{\{[^}\n]{1,120}\}\}|%[sd]|\{[A-Za-z_][\w.]*\}|\{\d?\}"
URL_TEMPLATE = (
    r"(?i)SCHEME://(?:[^\s/@\"'<>]{1,80}@)?(?P<host>" + HOST_CHARS + "|" + HOST_TEMPLATE + r"|\[[0-9a-fA-F:]+\])"
    r"(?::(?P<port>\d+|" + HOST_TEMPLATE + r"))?(?P<rest>[^\s\"'<>`)\]},;]*)")
HTTP_URL = re.compile(URL_TEMPLATE.replace("SCHEME", "http"))
HTTPS_URL = re.compile(URL_TEMPLATE.replace("SCHEME", "https"))
# A plain-HTTP address put together at run time: the scheme with no host after it.
HTTP_BUILT = re.compile(
    r"(?i)[\"'`]http:(?://)?[\"'`]\s*(?:\+|\.\s*concat\b)"
    r"|[\"'`]http[\"'`]\s*\+\s*[\"'`]:"
    r"|\bscheme\s*\(\s*[\"']http[\"']\s*\)"
    r"|new\s+(?:[\w.]+\.)?(?:URL|URI)\s*\(\s*[\"']http[\"']\s*,"
    r"|\bHttpHost\s*\(\s*[\"']http[\"']\s*,"
    r"|\bHttpHost\s*\([^()\n]{0,120},\s*[\"']http[\"']\s*\)")
# The key may start with a dash only right after a quote: a dash before it
# belongs to the leading run, so no dash can be read two ways (S-04).
SCHEME_KEY = re.compile(r"(?im)^[ \t-]*[\"']?(?:(?<=[\"'])-[\w.\-]*|[\w.][\w.\-]*)?(?:scheme|protocol)[\"']?[ \t]*[:=][ \t]*[\"']?http[\"']?[ \t]*(?:#[^\n]*)?$")
# Tried only at a quote or where a key starts, never inside a key: the first
# key ending in host or hostname is the same, found in one pass (S-04).
HOST_KEY = re.compile(r"(?i)(?:[\"']|(?<![\w.\-]))[\w.\-]*host(?:name)?[\"']?[ \t]*[:=][ \t]*[\"']?(" + HOST_CHARS + r")")
# Identifiers that look like URLs but are never called: XML namespaces,
# schema locations and licence links.
NON_ENDPOINT_HOSTS = {
    "www.w3.org", "w3.org", "maven.apache.org", "www.apache.org", "apache.org", "xmlns.jcp.org",
    "java.sun.com", "xmlns.oracle.com", "schemas.xmlsoap.org", "schemas.microsoft.com",
    "www.springframework.org", "json-schema.org", "opensource.org", "www.opensource.org",
    "www.gnu.org", "purl.org", "xml.org", "www.xml.org", "relaxng.org", "docbook.org",
    "ns.adobe.com", "schemas.openxmlformats.org", "www.eclipse.org", "jakarta.ee",
    "mybatis.org", "logback.qos.ch", "www.hibernate.org", "hibernate.org",
    "example.com", "example.org", "example.net",
}
# Plain-HTTP calls written without an http:// address (Q-16). The host is read
# when it is a literal; otherwise the call is "built" (decided at run time).
# Python's http.client (and urllib3's pool); HTTPS forms have an S.
PY_HTTP_CONNECTION = re.compile(
    r"\bHTTPConnection(?:Pool)?\s*\(\s*(?:host\s*=\s*)?(?:(?P<q>[\"'])(?P<host>" + HOST_CHARS + r")(?::(?P<port>\d{1,5}))?(?P=q)"
    r"(?:\s*,\s*(?:port\s*=\s*)?(?P<port2>\d{1,5}))?)?")
# Node's http module called with an options object (https.get is another name).
NODE_HTTP_OPTIONS = re.compile(r"(?<![\w.$])http\.(?:get|request)\s*\(\s*\{")
NODE_OPTION_KEY = re.compile(r"(?<![\w$.])[\"']?(?:host|hostname|port)[\"']?\s*[:,}]")
NODE_HOST_VALUE = re.compile(r"(?<![\w$.])[\"']?host(?:name)?[\"']?\s*:\s*[\"'](?P<host>" + HOST_CHARS + r")[\"']")
NODE_PORT_VALUE = re.compile(r"(?<![\w$.])[\"']?port[\"']?\s*:\s*[\"']?(?P<port>\d{1,5})\b")
# Go's url.URL composite literal; its fields can come in any order.
GO_URL_LITERAL = re.compile(r"\burl\.URL\s*\{")
GO_SCHEME_HTTP = re.compile(r"\bScheme\s*:\s*\"http\"")
GO_HOST_VALUE = re.compile(r"\bHost\s*:\s*\"(?P<host>" + HOST_CHARS + r")(?::(?P<port>\d{1,5}))?\"")
# .NET: UriBuilder("http", host[, port]), the scheme constant, and the property set
# on a builder (C#) or a url.URL value (Go).
DOTNET_URI_BUILDER = re.compile(
    r"\bnew\s+UriBuilder\s*\(\s*(?:\"http\"|Uri\.UriSchemeHttp\b)(?:\s*,\s*\"(?P<host>" + HOST_CHARS + r")\""
    r"(?:\s*,\s*(?P<port>\d{1,5}))?)?")
SCHEME_PROPERTY = re.compile(r"\.Scheme\s*=\s*(?:\"http\"|Uri\.UriSchemeHttp\b)")
XML_FILE = re.compile(r"\.(xml|xsd|wsdl|xsl|xslt|pom|xhtml|jspx|tld)$", re.I)
XML_NAME_ATTR = re.compile(
    r"(?<![\w.:-])(?:xmlns(?::[\w.-]+)?|(?:xsi:)?(?:noNamespace)?schemaLocation)\s*=\s*(\"[^\"]{0,4000}\"|'[^']{0,4000}')", re.S)
XML_DOCTYPE = re.compile(r"<!DOCTYPE\s+[\w:.-]+\s+(?:PUBLIC|SYSTEM)\s[^>\[]{0,2000}>", re.S)

# (rule id, pattern, severity). Severity "review" is for forms that are often
# harmless outside the HTTP service being migrated. Every repetition is
# bounded, so one long line costs time in proportion to its length.
_ARGS = r"[^;{}]{0,240}?"
_TRUE = r"(?:true|Boolean\.TRUE)\b"
_NOOP_BODY = r"\{\s*(?:/\*[^*]{0,200}\*/\s*|//[^\n]{0,200}\n\s*|return\s*;\s*){0,6}\}"
# The .NET properties that take a certificate validation callback.
_DOTNET_CALLBACK = r"(?:ServerCertificateCustomValidationCallback|ServerCertificateValidationCallback|RemoteCertificateValidationCallback)"
# A block whose only statement is "return true;", one line comment allowed before it.
_TRUE_BLOCK = r"\{\s*(?://[^\n]{0,200}\n\s*)?return\s+true\s*;\s*\}"
VERIFY_OFF_RULES: list[tuple[str, re.Pattern[str], str]] = [
    ("java-trust-all", re.compile(
        r"TrustAllStrategy|TrustSelfSignedStrategy|InsecureTrustManagerFactory|trustAllCerts"
        r"|X509(?:Extended)?TrustManager\s*\(\s*\)\s*\{"
        r"|loadTrustMaterial\s*\(" + _ARGS + r"(?:->|::|new\s+TrustStrategy)"
        r"|TrustStrategy\s+\w+\s*=\s*\([^)]{0,200}\)\s*->"
        r"|new\s+TrustStrategy\s*\(\s*\)\s*\{[^}]{0,300}?return\s+true"
        r"|addInsecureHost\s*\("
        r"|setTrustAll\s*\(\s*true\s*\)|setVerifyHost\s*\(\s*false\s*\)"
        r"|(?i:(?<![\w-])(?:trust-?all|insecure-?trust-?all-?certificates)[\"']?\s*[:=]\s*[\"']?true)"
        r"|(?i:(?<![\w-])verify-?host[\"']?\s*[:=]\s*[\"']?false)", re.S), "fail"),
    ("java-empty-check", re.compile(
        r"check(?:Server|Client)Trusted\s*\([^)]{0,300}\)\s*(?:throws\s+[\w.,\s]{1,200}?)?" + _NOOP_BODY +
        r"|check(?:Server|Client)Trusted\s*\([^)]{0,300}\)\s*(?::\s*Unit\s*)?=\s*Unit\b"
        r"|check(?:Server|Client)Trusted\s*:\s*\{[^{}]{0,80}->\s*\}", re.S), "fail"),
    ("java-hostname-off", re.compile(
        r"NoopHostnameVerifier|ALLOW_ALL_HOSTNAME_VERIFIER|AllowAllHostnameVerifier"
        r"|(?:[Hh]ostnameVerifier|SSLConnectionSocketFactory|SSLSocketFactory|TlsStrategy)\b" + _ARGS +
        r"->\s*(?:\{\s*return\s+)?" + _TRUE +
        r"|[Hh]ostnameVerifier\s*\{[^{}]{0,80}->\s*true\s*\}"
        r"|\{[^{}]{0,80}->\s*true\s*\}\s*as\s+HostnameVerifier"
        r"|boolean\s+verify\s*\(\s*(?:final\s+)?String\s+\w+\s*,\s*(?:final\s+)?SSLSession\s+\w+\s*\)\s*\{\s*return\s+true\s*;", re.S), "fail"),
    ("java-endpoint-id-off", re.compile(
        r"[eE]ndpointIdentificationAlgorithm\s*\(\s*(?:null|\"\")\s*\)|jdk\.internal\.httpclient\.disableHostnameVerification"), "fail"),
    ("spring-validation-off", re.compile(
        r"(?i)use[-_]?insecure[-_]?trust[-_]?manager[\"']?\s*[:=(]\s*[\"']?true"
        r"|(?i:disable[-_]?ssl[-_]?validation[\"']?\s*[:=]\s*[\"']?true)"), "fail"),
    ("client-auth-off", re.compile(
        r"(?i)server[._]ssl[._]client[-_]?auth[\"']?\s*[:=]\s*[\"']?none\b|setNeedClientAuth\s*\(\s*false\s*\)"
        # setClientAuth(ClientAuth.WANT), fully qualified, or WANT after a static import; the
        # Kotlin property form; Tomcat's connector property.
        r"|setClientAuth\s*\(\s*(?:[\w.]*\.)?(?:NONE|WANT)\s*\)"
        r"|\bclientAuth\s*=\s*(?:[\w.]*\.)?ClientAuth\.(?:NONE|WANT)\b"
        r"|setProperty\s*\(\s*\"clientAuth\"\s*,\s*\"(?:want|false|none|optional)\"\s*\)"
        r"|(?i:setCertificateVerification\s*\(\s*[\"'](?:none|optional|optional_no_ca)[\"']\s*\))"), "fail"),
    # A bare "client-auth: none" may belong to Kafka or another listener; E12
    # reads the producer's own setting, so here it is listed for review.
    ("client-auth-none-elsewhere", re.compile(r"(?i)(?<![.\w])client[-_.]?auth\s*[:=]\s*[\"']?none\b"), "review"),
    ("skip-verify", re.compile(
        r"(?i)insecure[-_]?skip[-_]?(?:tls[-_]?)?verify[\"']?\s*[:=]\s*[\"']?true"
        r"|(?i:proxy[-_]ssl[-_]verify[\"']?\s*:?\s*[\"']?off\b)"
        r"|(?i:auth-tls-verify-client[\"']?\s*:\s*[\"']?(?:off|optional_no_ca)\b)"
        r"|(?i:ssl_verify_client\s+(?:off|optional_no_ca)\b)"), "fail"),
    # Go: the field set from anything but the literal false (a variable, a call,
    # a negation): it can be true at run time (Q-16). "true" is the rule above.
    ("skip-verify", re.compile(r"\bInsecureSkipVerify\s*(?::|=(?!=))\s*(?!(?:false|true)\b)[\w!(&*]"), "fail"),
    # Envoy: an upstream or downstream validation context that accepts any chain.
    ("envoy-accept-untrusted", re.compile(
        r"(?:trust_chain_verification|trustChainVerification)[\"']?\s*:\s*[\"']?ACCEPT_UNTRUSTED\b"), "fail"),
    # Istio: a DestinationRule (tls) or PeerAuthentication (mtls) with TLS off,
    # block or flow style. Each line in between is matched from its first
    # character, so no space can be read two ways (S-04).
    ("mesh-tls-off", re.compile(
        r"(?m)^[ \t]*(?:-[ \t]*)?[\"']?m?tls[\"']?[ \t]*:[ \t]*(?:#[^\n]{0,200})?\n"
        r"(?:[ \t][^\n]{0,200}\n){0,8}?[ \t]+[\"']?mode[\"']?[ \t]*:[ \t]*[\"']?DISABLE\b"
        r"|[\"']?\bm?tls[\"']?[ \t]*:[ \t]*\{[^{}\n]{0,200}?\bmode[\"']?[ \t]*:[ \t]*[\"']?DISABLE\b"), "fail"),
    # ingress-nginx talking to the service behind it in plain HTTP or plain gRPC.
    ("ingress-backend-plain", re.compile(
        r"(?<![\w-])backend-protocol[\"']?[ \t]*:[ \t]*[\"']?(?i:http|grpc)\b"), "fail"),
    ("node-reject-off", re.compile(
        r"[\"']?rejectUnauthorized[\"']?\s*[:=]\s*false|[\"']?strictSSL[\"']?\s*[:=]\s*false"
        r"|NODE_TLS_REJECT_UNAUTHORIZED\s*=?\s*['\"]?0"), "fail"),
    ("python-verify-off", re.compile(
        r"verify\s*=\s*False|CERT_NONE|_create_unverified_context|check_hostname\s*=\s*False|PYTHONHTTPSVERIFY\s*=\s*['\"]?0"
        r"|(?<![\w.])(?:verify_)?ssl\s*=\s*False\b"), "fail"),
    ("dotnet-accept-any", re.compile(
        r"DangerousAcceptAnyServerCertificateValidator|ServerCertificateCustomValidationCallback\s*=\s*\([^)]{0,200}\)\s*=>\s*true"
        r"|ServerCertificateValidationCallback\s*[+]?=\s*[^;]{0,200}=>\s*true"
        # A lambda with a block body whose only statement is "return true", an
        # anonymous delegate doing the same, and the one-parameter lambda (Q-16).
        r"|" + _DOTNET_CALLBACK + r"\s*\+?=\s*(?:\([^)]{0,200}\)|[A-Za-z_]\w*)\s*=>\s*(?:true\b|" + _TRUE_BLOCK + r")"
        r"|" + _DOTNET_CALLBACK + r"\s*\+?=\s*delegate\b[^{;]{0,200}" + _TRUE_BLOCK), "fail"),
    ("curl-insecure", re.compile(
        r"(?:^|[\s\"'`(])curl\b(?:\\\r?\n|[^\n|;&]){0,400}?\s(?:-[a-zA-Z]{0,12}k[a-zA-Z]{0,12}|--insecure)(?=\s|$|[\"'`)])"
        r"|--no-check-certificate|CURLOPT_SSL_VERIFY(?:PEER|HOST)[^\n]{0,80}(?:\b0\b|false)"
        r"|-Dcom\.sun\.net\.ssl\.checkRevocation=false", re.M), "fail"),
    ("tls-old-protocol", re.compile(
        r"(?i)(?:enabled[-_]?protocols|ssl[-_]?protocols?|minimum_tls_version|MinVersion|jdk\.tls\.client\.protocols|https\.protocols)"
        r"[^\n]{0,200}?(?:TLSv1(?:\.0|\.1)?\b|SSLv3|VersionTLS10|VersionTLS11)(?!\.[23])"), "fail"),
    # The same, written as a YAML list on the following lines.
    ("tls-old-protocol", re.compile(
        r"(?im)^[ \t]*(?:-[ \t]*)?(?:enabled[-_]?protocols|ssl[-_]?protocols?|protocols)[ \t]*:[ \t]*(?:#[^\n]{0,200})?\n"
        r"(?:[ \t]*-[ \t]*[^\n]{0,80}\n){0,8}?[ \t]*-[ \t]*[\"']?(?:TLSv1(?:\.[01])?|SSLv3)[\"']?[ \t]*(?:#[^\n]{0,200})?$"), "fail"),
]

AI_DIRECTED = re.compile(
    r"(?i)(?:ignore (?:all |any |the )?(?:previous|prior|above) instructions"
    r"|(?:ai|assistant|copilot|claude|chatgpt|codex|llm|agent)s?\b[^\n]{0,60}\b(?:must|should|please)?\s*(?:skip|ignore|mark|treat|do not check|don't check|bypass)\b"
    r"|note to (?:the )?(?:ai|assistant|reviewer bot|llm))"
)
LOCAL_DEV = re.compile(r"local-dev-[a-z0-9-]+")

# ---------------------------------------------------------------- what was not read

SKIPPED: dict[tuple[str, str], bool] = {}


def reset_skipped() -> None:
    SKIPPED.clear()
    _TEXT_CACHE.clear()
    _OBJECT_CACHE.clear()
    _PLANNED_CACHE.clear()
    _WALK_CACHE.clear()
    _SQUASHED_CACHE.clear()


def note_skip(relative: str, reason: str, blocking: bool = False) -> None:
    key = (relative, reason)
    SKIPPED[key] = SKIPPED.get(key, False) or blocking


def skipped_report() -> dict[str, list[dict[str, str]]]:
    """Every file and folder the scans did not read, with the reason."""
    rows = sorted(SKIPPED.items())
    return {
        "blocking": [{"path": path, "reason": reason} for (path, reason), blocking in rows if blocking],
        "noted": [{"path": path, "reason": reason} for (path, reason), blocking in rows if not blocking],
    }


# ---------------------------------------------------------------- walking the tree

def _has_compiled(folder: Path) -> bool:
    seen = 0
    for _root, _dirs, files in os.walk(folder):
        for name in files:
            if name.endswith(COMPILED):
                return True
            seen += 1
            if seen > 2000:
                return False
    return False


def _is_build_output(parent: Path, name: str) -> bool:
    if name not in BUILD_OUTPUT:
        return False
    try:
        siblings = set(os.listdir(parent))
    except OSError:
        return False
    beside_build = bool(siblings & BUILD_FILES) or (
        name in ("bin", "obj") and any(s.endswith((".csproj", ".fsproj", ".vbproj", ".sln")) for s in siblings))
    if not beside_build:
        return False
    # Maven's target/ is output whatever it holds (it also keeps stale copies of
    # the resources); the other names only when they hold compiled files.
    return name == "target" or _has_compiled(parent / name)


_WALK_CACHE: dict[tuple[str, str], list[Path]] = {}


def iter_files(repo: Path, purpose: str = "code") -> Iterator[Path]:
    """purpose "code": what the migration changed (E2, E3, E12).
    purpose "certs": the code walk plus build output (E10): a local-dev CA a
    build put into target/ or a jar ships with the service.
    purpose "keys": everywhere a key could be left (E4): everything but the
    repository's own top-level .git (a nested folder called .git is read).
    Yields regular files, and links to files inside the repository. The tree
    is walked once per purpose and run; every scan shares the list."""
    key = (str(repo.resolve()), purpose)
    if key not in _WALK_CACHE:
        _WALK_CACHE[key] = list(_walk_files(repo, purpose))
    yield from _WALK_CACHE[key]


def _walk_files(repo: Path, purpose: str) -> Iterator[Path]:
    repo = repo.resolve()

    def unlisted(problem: OSError) -> None:
        # A folder that cannot be listed could hold a key or a setting: never skipped silently.
        where = Path(problem.filename) if problem.filename else repo
        try:
            relative = where.resolve().relative_to(repo).as_posix()
        except (ValueError, OSError):
            relative = str(where)
        note_skip(relative + "/", "a folder that could not be listed: it could hold a key or a setting", blocking=True)

    for root, dirs, files in os.walk(repo, onerror=unlisted):
        rel_root = Path(root).relative_to(repo).as_posix()
        kept = []
        for name in sorted(dirs):
            rel_dir = f"{rel_root}/{name}" if rel_root != "." else name
            path = Path(root) / name
            if name == ".git" and rel_root == ".":
                continue                      # the repository's own history; a nested .git folder is read
            if path.is_symlink():
                try:
                    inside = path.resolve().is_relative_to(repo)
                except OSError:
                    inside = False
                note_skip(rel_dir, "a link to a folder; its target is scanned where it really is" if inside
                          else "a link to a folder outside the repository: not scanned", blocking=not inside)
                continue
            if purpose in ("code", "certs"):
                if name == ".git":
                    note_skip(rel_dir + "/", "a nested .git folder: read by the key scan only")
                    continue
                if name in SKIP_ALWAYS:
                    note_skip(rel_dir + "/", "dependency cache, editor state or installer backup: read by the key scan only")
                    continue
                if name == "vendor" and set(os.listdir(root)) & VENDOR_MARKERS:
                    note_skip(rel_dir + "/", "vendored dependencies: read by the key scan only")
                    continue
                if SKILL_DIR.search(rel_dir):
                    note_skip(rel_dir + "/", "an installed skill (it quotes the patterns): read by the key scan only")
                    continue
                if purpose == "code" and _is_build_output(Path(root), name):
                    note_skip(rel_dir + "/", "build output: read by the key scan and the local-dev CA scan only")
                    continue
            kept.append(name)
        dirs[:] = kept
        for name in sorted(files):
            path = Path(root) / name
            relative = f"{rel_root}/{name}" if rel_root != "." else name
            try:
                mode = path.lstat().st_mode
            except OSError:
                note_skip(relative, "could not be read", blocking=True)
                continue
            if stat.S_ISLNK(mode):
                try:
                    target = path.resolve(strict=True)
                    inside = target.is_relative_to(repo)
                except OSError:
                    note_skip(relative, "a link that leads nowhere")
                    continue
                if not inside:
                    note_skip(relative, "a link to a file outside the repository: not scanned", blocking=True)
                    continue
                if not target.is_file():
                    note_skip(relative, "a link to something that is not a file")
                    continue
            elif not stat.S_ISREG(mode):
                note_skip(relative, "not a regular file (pipe, socket or device): not opened")
                continue
            if purpose in ("code", "certs") and WORKING_SKIP.search(relative):
                note_skip("tls-migration/ (reports, plans, evidence)", "the run's own records quote URLs and patterns on purpose")
                continue
            yield path


# ---------------------------------------------------------------- reading files

_TEXT_CACHE: dict[str, str | None] = {}
ESCAPED_CHAR = re.compile(r"\\u+([0-9a-fA-F]{4})")


def _unescape(match: re.Match[str]) -> str:
    char = chr(int(match.group(1), 16))
    return match.group(0) if char in "\r\n" else char


def read_text(path: Path) -> str | None:
    """The file as text, or None when it is not text. UTF-16 is decoded, stray NUL
    bytes are dropped (a NUL inside a comment does not turn source into a
    binary), and \\uXXXX escapes are resolved the way a compiler would."""
    key = str(path)
    if key in _TEXT_CACHE:
        return _TEXT_CACHE[key]
    text = _read_text(path)
    _TEXT_CACHE[key] = text
    return text


# Files that are text by their name: configuration, scripts, sources, deployment
# descriptors. Never taken for a binary, whatever bytes they hold.
TEXT_SUFFIXES = {".properties", ".yml", ".yaml", ".json", ".jsonc", ".env", ".conf", ".cfg", ".ini", ".toml", ".xml",
                 ".sh", ".bash", ".zsh", ".ps1", ".java", ".kt", ".kts", ".groovy", ".gradle", ".scala", ".py", ".js", ".ts",
                 ".mjs", ".cjs", ".go", ".rb", ".cs", ".tf", ".tfvars", ".hcl", ".tpl", ".md", ".txt", ".dockerfile"}
TEXT_NAMES = {"dockerfile", "containerfile", "makefile", "jenkinsfile", "procfile"}


def text_by_name(name: str) -> bool:
    lowered = name.lower()
    return os.path.splitext(lowered)[1] in TEXT_SUFFIXES or lowered in TEXT_NAMES or lowered.startswith((".env", "dockerfile")) \
        or bool(tlslib.CONFIG_NAME.match(name))


def _read_text(path: Path) -> str | None:
    try:
        size = path.stat().st_size
        if size > MAX_BYTES:
            note_skip(str(path), f"larger than {MAX_BYTES // 1_000_000} MB: searched for key markers only", blocking=True)
            return None
        data = path.read_bytes()
    except OSError:
        note_skip(str(path), "could not be read", blocking=True)
        return None
    text = decode_text(data)
    if text is None and text_by_name(path.name):
        # A configuration or source file with many NUL bytes (in a comment, say) is still
        # read by the service: Spring keeps a NUL as an ordinary character. It is read
        # here with the NUL bytes left out, and listed as blocking, so a setting or an
        # address behind them is never hidden by calling the file a binary.
        note_skip(str(path), "holds NUL bytes, unusual in a text file of this kind: read with them left out; "
                  "check what the service really reads", blocking=True)
        text = data.replace(b"\0", b"").decode("utf-8", errors="replace")
        if "\\u" in text:
            text = ESCAPED_CHAR.sub(_unescape, text)
    return text


def decode_text(data: bytes) -> str | None:
    """Bytes as text the way read_text reads a file, or None for a binary."""
    head = data[:8192]
    if head[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = data.decode("utf-16", errors="replace")
    elif b"\0" in head:
        nul = head.count(b"\0")
        if nul > len(head) // 4 and (head[1::2].count(b"\0") > len(head) // 3 or head[0::2].count(b"\0") > len(head) // 3):
            text = data.decode("utf-16-le" if head[1::2].count(b"\0") >= head[0::2].count(b"\0") else "utf-16-be", errors="replace")
        else:
            rest = head.replace(b"\0", b"")
            printable = sum(1 for byte in rest if byte in (9, 10, 13) or 32 <= byte < 127 or byte >= 128)
            if nul > len(head) // 20 or printable < len(rest) * 0.95:
                return None                     # a real binary: left to the key and certificate sniffers
            text = data.replace(b"\0", b"").decode("utf-8", errors="replace")
    else:
        text = data.decode("utf-8", errors="replace")
    if "\\u" in text:
        text = ESCAPED_CHAR.sub(_unescape, text)
    return text


_SQUASHED_CACHE: dict[str, str] = {}


def squashed_text(path: Path) -> str:
    """The file's text in tlslib.canonical form (letters and digits only, lower
    case), read once per run: how the config readers spot a setting's name in
    any of Spring's relaxed spellings before they parse anything."""
    key = str(path)
    if key not in _SQUASHED_CACHE:
        _SQUASHED_CACHE[key] = tlslib.canonical(read_text(path) or "")
    return _SQUASHED_CACHE[key]


def _continued(line: str) -> bool:
    return (len(line) - len(line.rstrip("\\"))) % 2 == 1


def join_continuations(text: str) -> str:
    """A .properties text with every value continued over several lines (a line
    ending in an odd number of backslashes) joined into one logical line, the
    way java.util.Properties reads it. The newlines taken out are put back
    after the joined line, so line numbers still hold. A comment is never
    continued."""
    lines = text.split("\n")
    out, index = [], 0
    while index < len(lines):
        line, start = lines[index].rstrip("\r"), index
        if not line.lstrip().startswith(("#", "!")):
            while _continued(line) and index + 1 < len(lines):
                index += 1
                line = line[:-1] + lines[index].rstrip("\r").lstrip(" \t\f")
        out.append(line + "\n" * (index - start))
        index += 1
    return "\n".join(out)


def rel(repo: Path, path: Path) -> str:
    try:
        return path.relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.resolve().relative_to(repo.resolve()).as_posix()


def _blank(match: re.Match[str]) -> str:
    """Replaces a match with spaces, keeping its newlines, so line numbers hold."""
    return re.sub(r"[^\n]", " ", match.group(0))


# ---------------------------------------------------------------- comments

# The tokens each syntax knows, tried in this order at every position, the way
# an alternation of regular expressions would try them (S-04): a
# triple-quoted string, a one-line string in double or single quotes (with
# backslash escapes), a backquoted string, and the comment forms. Read in one
# pass: an unclosed string or comment was once read again from every later
# quote or comment sign, which took time growing with the square of the text.
_LEXERS = {
    "c": ("dq3", "dq", "sq", "bt", "line//", "block"),
    "hash": ("dq3", "sq3", "dq", "sq", "hash"),
    "sql": ("dq", "sq", "line--", "block"),
    "xml": ("xml",),
    "dq": ("dq",),
}
_LEX_STARTS = {
    "c": re.compile(r"[\"'`]|/[/*]"),
    "hash": re.compile(r"[\"'#]"),
    "sql": re.compile(r"[\"']|--|/\*"),
    "xml": re.compile(r"<!--"),
    "dq": re.compile(r'"'),
}
_DQ_LINE_BODY = re.compile(r'[^"\\\n]*(?:\\.[^"\\\n]*)*')
_SQ_LINE_BODY = re.compile(r"[^'\\\n]*(?:\\.[^'\\\n]*)*")
_LEX_PROPS = re.compile(r"^[ \t]*[#!;][^\n]*", re.M)
_LEX_LINE_ONLY = re.compile(r"^[ \t]*(?://|#)[^\n]*", re.M)
_C_LIKE = {".java", ".kt", ".kts", ".groovy", ".gradle", ".scala", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".go",
           ".cs", ".c", ".cc", ".cpp", ".h", ".hpp", ".swift", ".rs", ".php", ".dart", ".json", ".jsonc", ".proto"}
_HASH = {".py", ".sh", ".bash", ".zsh", ".ksh", ".yml", ".yaml", ".toml", ".rb", ".tf", ".tfvars", ".pl", ".conf",
         ".cfg", ".env", ".mk", ".cmake", ".ps1", ".dockerfile", ".gitignore", ".editorconfig", ".hcl", ".nix"}
_HASH_NAMES = {"dockerfile", "makefile", "containerfile", "jenkinsfile", "vagrantfile", "procfile", "gemfile"}
_PROPS = {".properties", ".ini"}
_XML = {".xml", ".xsd", ".wsdl", ".xsl", ".xslt", ".pom", ".xhtml", ".jspx", ".tld", ".html", ".htm", ".svg", ".vue"}
_CLOSERS = {"dq3": '"""', "sq3": "'''", "bt": "`", "block": "*/", "xml": "-->"}
_OPENERS = {"dq3": '"""', "sq3": "'''", "dq": '"', "sq": "'", "bt": "`", "line//": "//", "line--": "--",
            "block": "/*", "xml": "<!--", "hash": "#"}


def lex_tokens(text: str, syntax: str) -> list[tuple[int, int]]:
    """(start, end) of every string and comment token of a text, left to right,
    without overlap: the tokens finditer finds over the alternation of the
    syntax's token patterns, found in time that grows with the text only."""
    kinds, starts = _LEXERS[syntax], _LEX_STARTS[syntax]
    size = len(text)
    # A closing mark searched for from a position and not found is not found
    # from any later one either; an unclosed one-line string stops where every
    # later quote before that place stops too (each was an escape inside it).
    no_close_from: dict[str, int] = {}
    unclosed_until: dict[str, int] = {}
    tokens: list[tuple[int, int]] = []

    def closing(kind: str, start: int) -> int:
        if start >= no_close_from.get(kind, size + 1):
            return -1
        mark = _CLOSERS[kind]
        found = text.find(mark, start)
        if found < 0:
            no_close_from[kind] = start
            return -1
        return found + len(mark)

    def line_string(kind: str, at: int) -> int:
        if at < unclosed_until.get(kind, -1):
            return -1
        quote = _OPENERS[kind]
        end = (_DQ_LINE_BODY if kind == "dq" else _SQ_LINE_BODY).match(text, at + 1).end()
        if end < size and text[end] == quote:
            return end + 1
        unclosed_until[kind] = end
        return -1

    def line_end(at: int) -> int:
        end = text.find("\n", at)
        return size if end < 0 else end

    def token_end(at: int) -> int:
        for kind in kinds:
            if not text.startswith(_OPENERS[kind], at):
                continue
            if kind in ("dq", "sq"):
                end = line_string(kind, at)
            elif kind in ("line//", "line--"):
                end = line_end(at)
            elif kind == "hash":
                end = line_end(at) if at == 0 or text[at - 1].isspace() else -1
            else:
                end = closing(kind, at + len(_OPENERS[kind]))
            if end >= 0:
                return end
        return -1

    position = 0
    while position < size:
        candidate = starts.search(text, position)
        if candidate is None:
            break
        at = candidate.start()
        end = token_end(at)
        if end < 0:
            position = at + 1
            continue
        tokens.append((at, end))
        position = end
    return tokens


def comment_spans(text: str, name: str) -> tuple[list[int], list[int]]:
    """Where the comments are, by the file's own syntax: a hit counts as "in a
    comment" only when it starts inside one, not when its line merely begins
    with a comment sign."""
    lowered = name.lower()
    suffix = os.path.splitext(lowered)[1]
    base = lowered.split(".")[0]
    if suffix in _C_LIKE:
        syntax, marks = "c", ("//", "/*")
    elif suffix in _PROPS:
        syntax, marks = _LEX_PROPS, None
    elif suffix in _XML:
        syntax, marks = "xml", None
    elif suffix == ".sql":
        syntax, marks = "sql", ("--", "/*")
    elif suffix in _HASH or base in _HASH_NAMES or lowered.startswith((".env", "dockerfile")) or text.startswith("#!"):
        syntax, marks = "hash", ("#",)
    else:
        # Unknown syntax: whole-line comments only.
        syntax, marks = _LEX_LINE_ONLY, None
    if isinstance(syntax, str):
        found = lex_tokens(text, syntax)
    else:                       # anchored at a line start: tried once per line
        found = [match.span() for match in syntax.finditer(text)]
    starts, ends = [], []
    for start, end in found:
        if marks is None or text.startswith(marks, start):
            starts.append(start)
            ends.append(end)
    return starts, ends


def in_comment(spans: tuple[list[int], list[int]], position: int) -> bool:
    starts, ends = spans
    index = bisect.bisect_right(starts, position) - 1
    return index >= 0 and position < ends[index]


# ---------------------------------------------------------------- URLs

def _join_shell_lines(text: str) -> str:
    """A shell script or Dockerfile with every backslash-newline taken out (the
    shell and Docker join those lines, inside double quotes too, indentation
    kept); the line breaks are put back after the joined line, so line numbers
    still hold."""
    lines = text.split("\n")
    out, index = [], 0
    while index < len(lines):
        line, start = lines[index].rstrip("\r"), index
        while _continued(line) and index + 1 < len(lines):
            index += 1
            line = line[:-1] + lines[index].rstrip("\r")
        out.append(line + "\n" * (index - start))
        index += 1
    return "\n".join(out)


# The inside of a YAML or JSON double-quoted scalar, which may run over several
# lines: written as one run of plain characters and escapes, so no character can
# be matched two ways (an unclosed quote of backslashes and line breaks once
# took exponential time; S-04).
_DOUBLE_QUOTED_BODY = re.compile(r'[^"\\]*(?:\\.[^"\\]*)*', re.S)


def double_quoted_spans(text: str) -> list[tuple[int, int]]:
    """(start, end) of every double-quoted scalar, quotes included, in one pass.
    A quote that is never closed ends the scan: every later quote lies inside
    it and could not close either, so nothing is missed."""
    spans, position = [], 0
    while True:
        start = text.find('"', position)
        if start < 0:
            return spans
        end = _DOUBLE_QUOTED_BODY.match(text, start + 1).end()
        if end >= len(text) or text[end] != '"':
            return spans
        spans.append((start, end + 1))
        position = end + 1
_YAML_ESCAPES = {"0": "\0", "a": "\a", "b": "\b", "t": "\t", "\t": "\t", "n": "\n", "v": "\v", "f": "\f", "r": "\r",
                 "e": "\x1b", " ": " ", '"': '"', "/": "/", "\\": "\\", "N": "\x85", "_": "\xa0", "L": "\u2028", "P": "\u2029"}


def decode_double_quoted(body: str) -> str:
    """A YAML 1.2 double-quoted scalar's content, decoded: \\xNN, \\uNNNN and
    \\UNNNNNNNN escapes, an escaped line break (the lines join with nothing
    between them) and line folding (a bare line break is a space)."""
    out, index = [], 0
    while index < len(body):
        char = body[index]
        if char == "\\" and index + 1 < len(body):
            nxt = body[index + 1]
            width = {"x": 2, "u": 4, "U": 8}.get(nxt)
            if width and re.fullmatch(r"[0-9a-fA-F]{%d}" % width, body[index + 2:index + 2 + width]):
                out.append(chr(int(body[index + 2:index + 2 + width], 16)))
                index += 2 + width
                continue
            if nxt in "\r\n":
                index += 2 if body[index + 1:index + 3] != "\r\n" else 3
                while index < len(body) and body[index] in " \t":
                    index += 1
                continue
            out.append(_YAML_ESCAPES.get(nxt, "\\" + nxt))
            index += 2
            continue
        if char == "\n":
            while out and out[-1] in " \t":
                out.pop()
            index += 1
            while index < len(body) and body[index] in " \t":
                index += 1
            out.append(" ")
            continue
        out.append(char)
        index += 1
    return "".join(out)


def _decoded_scalars(path: Path, text: str) -> list[tuple[int, str]]:
    """(offset, value) for every YAML/JSON string whose decoded value differs from
    how it is written (escapes, continued lines), plus, with PyYAML, every string
    value of the parsed documents: an address written with \\x68ttp or over two
    lines is the same address."""
    found = []
    for start, end in double_quoted_spans(text):
        body = text[start + 1:end - 1]
        if "\\" not in body and "\n" not in body:
            continue
        found.append((start, decode_double_quoted(body)))
    if tlslib._pyyaml is not None and path.suffix.lower() in (".yml", ".yaml", ".json"):  # noqa: SLF001
        try:
            documents = list(tlslib._pyyaml.safe_load_all(text))  # noqa: SLF001
        except Exception:  # noqa: BLE001 - a template or odd file: the text scan above still ran
            documents = []
        stack = list(documents)
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                stack += list(node.values())
            elif isinstance(node, list):
                stack += node
            elif isinstance(node, str) and node not in text:
                found.append((0, node))
    return found


OBJECT_LIMIT = 4000             # how much of an options object is read for its host and port


def http_calls(text: str) -> list[tuple[int, str, str, str]]:
    """(offset, host, port, what) for each plain-HTTP call written without an
    http:// address. host is "" when it is not a literal in the call."""
    found: list[tuple[int, str, str, str]] = []
    for match in PY_HTTP_CONNECTION.finditer(text):
        found.append((match.start(), match.group("host") or "", match.group("port") or match.group("port2") or "",
                      "http.client " + match.group(0).split("(", 1)[0].strip()))
    for match in DOTNET_URI_BUILDER.finditer(text):
        found.append((match.start(), match.group("host") or "", match.group("port") or "", 'UriBuilder("http", ...)'))
    for match in SCHEME_PROPERTY.finditer(text):
        found.append((match.start(), "", "", 'Scheme = "http"'))
    objects: list[tuple[int, str]] = []
    if "http." in text:
        objects += [(m.end() - 1, "node") for m in NODE_HTTP_OPTIONS.finditer(text)]
    if "url.URL" in text:
        objects += [(m.end() - 1, "go") for m in GO_URL_LITERAL.finditer(text)]
    if objects:
        # The object's own braces: the brace after the call is the opening one,
        # so the innermost pair around the next character is that object. Each
        # pattern is searched once over the whole text and looked up by offset,
        # so many (or nested, unclosed) objects cost no more than one pass.
        where = innermost_braces(text, [opened + 1 for opened, _ in objects])
        index: dict[str, tuple[list[int], list[re.Match[str]]]] = {}

        def first(pattern: re.Pattern[str], start: int, end: int) -> re.Match[str] | None:
            """The first match of the pattern that lies wholly between start and end."""
            if pattern.pattern not in index:
                matches = list(pattern.finditer(text))
                index[pattern.pattern] = ([m.start() for m in matches], matches)
            starts, matches = index[pattern.pattern]
            at = bisect.bisect_left(starts, start)
            return matches[at] if at < len(matches) and matches[at].end() <= end else None

        for opened, kind in objects:
            start, end = where.get(opened + 1, (opened, len(text)))
            end = min(end, start + OBJECT_LIMIT)
            if kind == "node":
                if not first(NODE_OPTION_KEY, start, end):
                    continue                    # no host or port given: not the call this rule is about
                host, port = first(NODE_HOST_VALUE, start, end), first(NODE_PORT_VALUE, start, end)
                found.append((opened, host.group("host") if host else "", port.group("port") if port else "",
                              "Node http options"))
            else:
                if not first(GO_SCHEME_HTTP, start, end):
                    continue
                host = first(GO_HOST_VALUE, start, end)
                found.append((opened, host.group("host") if host else "", (host.group("port") or "") if host else "",
                              'url.URL{Scheme: "http"}'))
    return found


def _url_hits(repo: Path, pattern: re.Pattern[str], needle: str, built: bool) -> list[dict[str, Any]]:
    found = []
    for path in iter_files(repo):
        text = read_text(path)
        if text is None or needle not in text.lower():
            continue
        suffix = path.suffix.lower()
        if suffix == ".properties":
            text = join_continuations(text)     # a value continued with \ is one address (lines kept)
        elif suffix in (".sh", ".bash", ".zsh") or path.name.lower().startswith(("dockerfile", "containerfile")) \
                or text.startswith("#!"):
            # A backslash before the line break joins the lines (inside double quotes too).
            text = _join_shell_lines(text)
        # Escaped separators (\: in .properties, \/ in JSON and YAML) are the same address.
        text = text.replace("\\/", "/").replace("\\:", ":")
        if XML_FILE.search(path.name) or text.lstrip().startswith("<?xml"):
            # Namespace names and DTD identifiers are never called, even across lines.
            text = XML_DOCTYPE.sub(_blank, XML_NAME_ATTR.sub(_blank, text))
        relative = rel(repo, path)
        spans = comment_spans(text, path.name)
        doc = bool(DOC_FILE.search(path.name))
        lines = text.splitlines()

        def hit(position: int, host: str, port: str, url: str, kind: str) -> None:
            number = text.count("\n", 0, position) + 1
            line = lines[number - 1] if number - 1 < len(lines) else ""
            found.append({"file": relative, "line": number, "host": host, "port": port, "url": url,
                          "text": line.strip()[:200], "doc": doc, "comment": in_comment(spans, position), "kind": kind})

        for match in pattern.finditer(text):
            host = match.group("host").lower().rstrip(".")
            if host in NON_ENDPOINT_HOSTS:
                continue
            templated = host[:1] in "${%"
            hit(match.start(), host, match.group("port") or "", match.group(0), "templated" if templated else "url")
        if path.suffix.lower() in (".yml", ".yaml", ".json"):
            seen_urls = {m.group(0) for m in pattern.finditer(text)}
            for offset, value in _decoded_scalars(path, text):
                for match in pattern.finditer(value):
                    host = match.group("host").lower().rstrip(".")
                    if host in NON_ENDPOINT_HOSTS or match.group(0) in seen_urls:
                        continue
                    seen_urls.add(match.group(0))
                    hit(offset, host, match.group("port") or "", match.group(0) + " (decoded from the file's escapes)",
                        "templated" if host[:1] in "${%" else "url")
        if not built:
            continue
        for match in HTTP_BUILT.finditer(text):
            hit(match.start(), "", "", match.group(0), "built")
        for position, host, port, what in http_calls(text):
            host = host.lower().rstrip(".")
            if host in NON_ENDPOINT_HOSTS:
                continue
            if host:                            # a literal host: judged by scope like any http:// address
                hit(position, host, port, f"http://{host}" + (f":{port}" if port else "") + f" ({what})", "url")
            else:
                hit(position, "", "", what, "built")
        for match in SCHEME_KEY.finditer(text):
            number = text.count("\n", 0, match.start()) + 1
            nearby = "\n".join(lines[max(0, number - 5):number + 4])
            host = HOST_KEY.search(nearby)
            if host:
                hit(match.start(), host.group(1).lower().rstrip("."), "", match.group(0).strip(), "scheme-key")
    return found


def find_http_urls(repo: Path) -> list[dict[str, Any]]:
    """Plain http:// addresses. kind "url": a literal host; "templated": the host
    is a placeholder; "built": the address is put together at run time;
    "scheme-key": scheme http and a host given as separate keys."""
    return _url_hits(repo, HTTP_URL, "http", built=True)


def find_https_urls(repo: Path) -> list[dict[str, Any]]:
    return _url_hits(repo, HTTPS_URL, "https://", built=False)


# ---------------------------------------------------------------- checking switched off

_BRACE = re.compile(r"[{}]")
# A server option: present only where Node is asked to act as a TLS server.
NODE_REQUEST_CERT = re.compile(r"[\"']?\brequestCert[\"']?\s*:\s*true\b")
# A validation callback given as a method group (or wrapped in the delegate's
# constructor); null keeps the default checks.
DOTNET_METHOD_GROUP = re.compile(
    _DOTNET_CALLBACK + r"\s*\+?=\s*(?:new\s+RemoteCertificateValidationCallback\s*\(\s*)?"
    r"(?P<name>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*){0,6})\s*(?:\)\s*)?;")
# A bool method whose whole body is "return true" (expression or block body).
DOTNET_TRUE_METHOD = re.compile(
    r"\bbool\s+(?P<name>[A-Za-z_]\w*)\s*\([^)]{0,400}\)\s*(?:=>\s*true\s*;|" + _TRUE_BLOCK + r")")


def innermost_braces(text: str, positions: list[int]) -> dict[int, tuple[int, int]]:
    """For each position, the (open, close) offsets of the innermost {...}
    around it; close is the text's end when the brace is never closed. One pass
    over the braces, whatever the number of positions (S-04)."""
    if not positions:
        return {}
    wanted = sorted(set(positions))
    found: dict[int, tuple[int, int]] = {}
    stack: list[int] = []
    waiting: list[list[int]] = [[]]        # positions inside the brace at the same depth of the stack
    index = 0
    for brace in _BRACE.finditer(text):
        at = brace.start()
        while index < len(wanted) and wanted[index] <= at:   # on a closing brace: inside the pair it closes
            waiting[-1].append(wanted[index])
            index += 1
        if brace.group(0) == "{":
            stack.append(at)
            waiting.append([])
        elif stack:
            opened = stack.pop()
            for position in waiting.pop():
                found[position] = (opened, at + 1)
    while index < len(wanted):
        waiting[-1].append(wanted[index])
        index += 1
    for opened, inside in zip(stack, waiting[1:]):
        for position in inside:
            found[position] = (opened, len(text))
    return found


def _extra_verify_off(text: str) -> list[tuple[int, str, str]]:
    """(offset, rule id, severity) for the forms a single pattern cannot judge."""
    found: list[tuple[int, str, str]] = []
    if "ValidationCallback" in text:
        always_true = {m.group("name") for m in DOTNET_TRUE_METHOD.finditer(text)}
        for match in DOTNET_METHOD_GROUP.finditer(text):
            name = match.group("name").rsplit(".", 1)[-1]
            if name in ("null", "DangerousAcceptAnyServerCertificateValidator"):
                continue
            # The method in this file returns true whatever the certificate: it
            # accepts any. Anything else is a person's (or the judge's) to read.
            found.append((match.start(), "dotnet-accept-any" if name in always_true else "dotnet-custom-validator",
                          "fail" if name in always_true else "review"))
    return found


def _server_reject_off(text: str, starts: list[int]) -> set[int]:
    """Of the rejectUnauthorized: false hits, those in the same options object as
    requestCert: true. That is a Node TLS server asking for a client
    certificate without requiring one: listed for review, while the same setting
    in a client's options (no requestCert there) fails."""
    if not starts or "requestCert" not in text:
        return set()
    servers = [m.start() for m in NODE_REQUEST_CERT.finditer(text)]
    where = innermost_braces(text, starts + servers)
    server_objects = {where[p] for p in servers if p in where}
    return {p for p in starts if where.get(p) in server_objects}


def find_verify_off(repo: Path) -> list[dict[str, Any]]:
    found = []
    for path in iter_files(repo):
        text = read_text(path)
        if text is None:
            continue
        if path.suffix.lower() == ".properties":
            text = join_continuations(text)     # a value continued with \ is one setting
        lines = text.splitlines()
        is_doc = bool(DOC_FILE.search(path.name))
        hits: list[tuple[int, str, str]] = []
        for rule_id, pattern, severity in VERIFY_OFF_RULES:
            for match in pattern.finditer(text):
                hits.append((match.start() + (len(match.group(0)) - len(match.group(0).lstrip())), rule_id, severity))
        servers = _server_reject_off(text, [start for start, rule_id, _ in hits if rule_id == "node-reject-off"
                                            and text.startswith(("rejectUnauthorized", "\"rejectUnauthorized", "'rejectUnauthorized"), start)])
        hits = [(start, "node-client-cert-optional", "review") if rule_id == "node-reject-off" and start in servers
                else (start, rule_id, severity) for start, rule_id, severity in hits]
        hits += _extra_verify_off(text)
        spans = None
        seen: set[tuple[int, str]] = set()
        breaks = [m.start() for m in re.finditer("\n", text)] if hits else []
        for start, rule_id, severity in hits:
            number = bisect.bisect_left(breaks, start) + 1
            if (number, rule_id) in seen:
                continue
            seen.add((number, rule_id))
            line = lines[number - 1] if number - 1 < len(lines) else ""
            if spans is None:
                spans = comment_spans(text, path.name)
            severity_here = "review" if is_doc or in_comment(spans, start) else severity
            found.append({"file": rel(repo, path), "line": number, "rule": rule_id, "severity": severity_here,
                          "text": line.strip()[:200]})
    # A line already failed by a stricter rule is not listed again for review.
    failed_lines = {(h["file"], h["line"]) for h in found if h["severity"] == "fail"}
    return [h for h in found if h["severity"] == "fail" or (h["file"], h["line"]) not in failed_lines]


# ---------------------------------------------------------------- keys, key stores, certificates

_OBJECT_CACHE: dict[str, list[tuple[str, int, Any]]] = {}


def _store_kind(head: bytes) -> str | None:
    if head[:4] in (b"\xfe\xed\xfe\xed", b"\xce\xce\xce\xce"):
        return "jks"
    if head[:1] == b"\x30" and b"\x02\x01\x03\x30" in head[:12]:
        return "pkcs12"
    return None


def _open_store(path: Path, kind: str) -> tuple[bool | None, list[str]]:
    """(holds a key, certificates as PEM). The first is None when the store could
    not be opened with an empty or a well-known password. No key is ever printed."""
    for password in STORE_PASSWORDS:
        if kind == "pkcs12":
            for extra in ([], ["-legacy"]):
                code, _, info = tlslib.run(["openssl", "pkcs12", "-in", str(path), "-info", "-noout", "-passin", f"pass:{password}", *extra], timeout=20)
                if code != 0:
                    continue
                has_key = bool(re.search(r"(?i)key ?bag", info))
                _, pems, _ = tlslib.run(["openssl", "pkcs12", "-in", str(path), "-nokeys", "-passin", f"pass:{password}", *extra], timeout=20)
                return has_key, tlslib.PEM_CERT.findall(pems)
        elif shutil.which("keytool"):
            code, listing, _ = tlslib.run(["keytool", "-list", "-rfc", "-keystore", str(path), "-storepass", password or "changeit"], timeout=30)
            if code == 0:
                return "PrivateKeyEntry" in listing or "SecretKeyEntry" in listing, tlslib.PEM_CERT.findall(listing)
    return None, []


def _looks_der(data: bytes) -> bool:
    """A DER SEQUENCE whose length field accounts for the whole blob (a few
    trailing bytes of padding or a newline allowed): cheap, and it keeps random
    base64-looking text away from openssl."""
    if data[:1] != b"\x30" or len(data) < 4:
        return False
    first = data[1]
    if first < 0x80:
        total = 2 + first
    elif first in (0x81, 0x82, 0x83):
        count = first - 0x80
        total = 2 + count + int.from_bytes(data[2:2 + count], "big")
    else:
        return False
    return total <= len(data) <= total + 4


# Password-based encryption of a PKCS#8 key (EncryptedPrivateKeyInfo): PBES2
# (1.2.840.113549.1.5.13), the PKCS#5 v1.5 schemes (1.2.840.113549.1.5.1-11)
# and the PKCS#12 ones (1.2.840.113549.1.12.1.1-6), as DER object identifiers.
PBES_OID = re.compile(rb"^\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x05[\x01-\x0d]$"
                      rb"|^\x06\x0a\x2a\x86\x48\x86\xf7\x0d\x01\x0c\x01[\x01-\x06]$")


def _der_item(data: bytes, offset: int) -> tuple[int, int, int] | None:
    """(tag, start of the content, end of the content) of the DER item at offset."""
    if offset + 2 > len(data):
        return None
    tag, first = data[offset], data[offset + 1]
    start = offset + 2
    if first < 0x80:
        length = first
    elif 0x81 <= first <= 0x83:
        count = first - 0x80
        if start + count > len(data):
            return None
        length = int.from_bytes(data[start:start + count], "big")
        start += count
    else:
        return None
    end = start + length
    return (tag, start, end) if end <= len(data) else None


def encrypted_key_scheme(data: bytes) -> bool:
    """True for a password-encrypted PKCS#8 key in DER: SEQUENCE { SEQUENCE {
    a password-based encryption OID, parameters }, OCTET STRING }. Shape and
    OID only: nothing is decrypted, and no password is tried."""
    outer = _der_item(data, 0)
    if not outer or outer[0] != 0x30:
        return False
    algorithm = _der_item(data, outer[1])
    if not algorithm or algorithm[0] != 0x30:
        return False
    oid = _der_item(data, algorithm[1])
    if not oid or oid[0] != 0x06 or not PBES_OID.match(data[algorithm[1]:oid[2]]):
        return False
    payload = _der_item(data, algorithm[2])
    return bool(payload) and payload[0] == 0x04 and payload[2] == outer[2] and payload[2] > payload[1]


# The start of a DER certificate: a SEQUENCE holding the to-be-signed SEQUENCE,
# whose first item is the explicit version (v1, v2 or v3). Fixed-width, so the
# search stays linear.
DER_CERT_START = re.compile(rb"\x30(?:\x81.|\x82..)\x30(?:\x81.|\x82..)\xa0\x03\x02\x01[\x00-\x02]", re.S)
MAX_INNER_CERTS = 16


def _inner_der_certs(data: bytes) -> list[tuple[str, Any]]:
    """Certificates in DER that do not start the blob: bytes before them (a
    header, a line of text such as the warning OpenSSL 4 writes into the output
    of `x509 -trustout -outform DER`, a container) do not hide them. Trust
    settings after a certificate are ignored, as for a DER file."""
    found: list[tuple[str, Any]] = []
    tried = 0
    for match in DER_CERT_START.finditer(data):
        if match.start() == 0:
            continue                         # the blob as a whole was read already
        head = match.group(0)
        size = 3 + head[2] if head[1] == 0x81 else 4 + int.from_bytes(head[2:4], "big")
        if size < 40 or match.start() + size > len(data):
            continue                         # no whole certificate fits here
        leading = data[match.start():match.start() + size]
        tried += 1
        if tried > MAX_INNER_CERTS:
            # Never skipped silently: the rest of the file was not read for certificates.
            found.append(("unread", f"more than {MAX_INNER_CERTS} embedded DER certificates: "
                                    "only the first ones were read"))
            break
        with tempfile.NamedTemporaryFile(suffix=".der") as handle:
            handle.write(leading)
            handle.flush()
            code, pem, _ = tlslib.run(["openssl", "x509", "-inform", "DER", "-in", handle.name], timeout=10)
        if code == 0 and "BEGIN CERTIFICATE" in pem:
            found.append(("cert", pem))
    return found


def _der_objects(data: bytes) -> list[tuple[str, Any]]:
    """What a DER blob is: a private key (an encrypted one included), a
    certificate (also one followed by trust settings), or nothing we know."""
    if not 40 <= len(data) <= 20_000:
        return []
    if not _looks_der(data):
        leading = tlslib._leading_der(data)  # noqa: SLF001 - the same DER rule, shared
        if leading is None or len(leading) < 40:
            return []
        with tempfile.NamedTemporaryFile(suffix=".der") as handle:
            handle.write(leading)
            handle.flush()
            code, pem, _ = tlslib.run(["openssl", "x509", "-inform", "DER", "-in", handle.name], timeout=10)
        return [("cert", pem)] if code == 0 else []
    if encrypted_key_scheme(data):
        return [("key", "DER-encoded password-encrypted private key (PKCS#8)")]
    with tempfile.NamedTemporaryFile(suffix=".der") as handle:
        handle.write(data)
        handle.flush()
        code, _, _ = tlslib.run(["openssl", "pkey", "-inform", "DER", "-in", handle.name, "-noout", "-passin", "pass:"], timeout=10)
        if code == 0:
            return [("key", "DER-encoded private key")]
        code, pem, _ = tlslib.run(["openssl", "x509", "-inform", "DER", "-in", handle.name], timeout=10)
        if code == 0:
            return [("cert", pem)]
    return []


def _flat(pem: str) -> str:
    return "".join(pem.split())


def public_of_key(data: bytes) -> str | None:
    """The public half of a private key (PEM or DER), as one line of text, or None
    when it cannot be derived (encrypted, or a format openssl pkey does not read).
    Only the public key is printed; it is what lets a key be compared with the
    certificates the migration planned."""
    with tempfile.NamedTemporaryFile(suffix=".key") as handle:
        handle.write(data)
        handle.flush()
        form = [] if KEY_MARKER.search(data) else ["-inform", "DER"]
        code, public, _ = tlslib.run(["openssl", "pkey", "-in", handle.name, *form, "-pubout", "-passin", "pass:"], timeout=10)
    return _flat(public) if code == 0 and "PUBLIC KEY" in public else None


def public_of_cert(pem: str) -> str | None:
    code, public, _ = tlslib.run(["openssl", "x509", "-pubkey", "-noout"], stdin=pem, timeout=10)
    return _flat(public) if code == 0 and "PUBLIC KEY" in public else None


# A JSON Web Key holding a private key: "kty" RSA, EC or OKP with a "d" member
# (inside a JWKS, a JSON value in YAML, or code). A public JWK has no "d".
JWK_KTY = re.compile(r"""(?:(?<=[{,\s])|^)["']?kty["']?\s*:\s*["']?(RSA|EC|OKP)\b""")
JWK_MEMBER = re.compile(r"""(?:(?<=[{,\s])|^)["']?(d|n|e|crv|x|y)["']?\s*:\s*["']([A-Za-z0-9_\-+/=]+)["']""")
JWK_CURVES = {"P-256": ("06082a8648ce3d030107", 32), "P-384": ("06052b81040022", 48), "P-521": ("06052b81040023", 66)}
JWK_OKP = {"Ed25519": "06032b6570", "X25519": "06032b656e", "Ed448": "06032b6571", "X448": "06032b656f"}


def _der(tag: int, body: bytes) -> bytes:
    size = len(body)
    length = bytes([size]) if size < 0x80 else bytes([0x80 | ((size.bit_length() + 7) // 8)]) + size.to_bytes((size.bit_length() + 7) // 8, "big")
    return bytes([tag]) + length + body


def _b64url(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _jwk_public(kty: str, members: dict[str, str]) -> str | None:
    """The public key of a private JWK, as openssl prints it (one line), so it can
    be compared with the planned certificates; None when it cannot be built."""
    try:
        if kty == "RSA":
            numbers = b"".join(_der(0x02, b"\x00" + _b64url(members[k]).lstrip(b"\x00")) for k in ("n", "e"))
            spki = _der(0x30, _der(0x30, bytes.fromhex("06092a864886f70d010101") + b"\x05\x00")
                        + _der(0x03, b"\x00" + _der(0x30, numbers)))
        elif kty == "EC":
            oid, size = JWK_CURVES[members["crv"]]
            point = b"\x04" + _b64url(members["x"]).rjust(size, b"\x00") + _b64url(members["y"]).rjust(size, b"\x00")
            if len(point) != 1 + 2 * size:
                return None
            spki = _der(0x30, _der(0x30, bytes.fromhex("06072a8648ce3d0201" + oid)) + _der(0x03, b"\x00" + point))
        else:
            spki = _der(0x30, _der(0x30, bytes.fromhex(JWK_OKP[members["crv"]])) + _der(0x03, b"\x00" + _b64url(members["x"])))
    except (KeyError, ValueError, binascii.Error):
        return None
    with tempfile.NamedTemporaryFile(suffix=".der") as handle:
        handle.write(spki)
        handle.flush()
        code, public, _ = tlslib.run(["openssl", "pkey", "-pubin", "-inform", "DER", "-in", handle.name, "-pubout"], timeout=10)
    return _flat(public) if code == 0 and "PUBLIC KEY" in public else None


def _jwk_objects(text: str) -> list[tuple[int, str, Any]]:
    """Private JWKs in a text: (offset, "key", reason) and (offset, "public", its public key)."""
    found: list[tuple[int, str, Any]] = []
    if "kty" not in text:
        return found
    for match in JWK_KTY.finditer(text):
        start = text.rfind("{", max(0, match.start() - 20_000), match.start())
        if start < 0:
            continue
        depth, end = 0, len(text)
        for index in range(start, min(len(text), start + 40_000)):
            depth += {"{": 1, "}": -1}.get(text[index], 0)
            if depth == 0:
                end = index + 1
                break
        members: dict[str, str] = {}
        for member in JWK_MEMBER.finditer(text, start + 1, end):
            members.setdefault(member.group(1), member.group(2))
        if len(members.get("d", "")) < 16:
            continue
        found.append((start, "key", f"JSON Web Key with a private part (kty {match.group(1)} with d)"))
        public = _jwk_public(match.group(1), members)
        if public:
            found.append((start, "public", public))
    return found


def _binary_objects(data: bytes, what: str) -> list[tuple[str, Any]]:
    """Keys, key stores and certificates in a blob of bytes (a file, a decoded
    base64 value, an archive member). A key that can be read also yields
    ("public", its public key), so it can be matched to a planned certificate."""
    found = _binary_objects_raw(data, what)
    if any(kind == "key" for kind, _ in found) and not _store_kind(data[:16]):
        public = public_of_key(data)
        if public:
            found.append(("public", public))
    return found


def _binary_objects_raw(data: bytes, what: str) -> list[tuple[str, Any]]:
    found: list[tuple[str, Any]] = []
    kind = _store_kind(data[:16])
    if kind:
        with tempfile.NamedTemporaryFile(suffix=".store") as handle:
            handle.write(data)
            handle.flush()
            has_key, pems = _open_store(Path(handle.name), kind)
        if has_key is None:
            found.append(("key", f"{what}: a key store that could not be opened to show it holds no key"))
        elif has_key:
            found.append(("key", f"{what}: a key store holding a private key"))
        found += [("cert", pem) for pem in pems]
        return found
    if KEY_MARKER.search(data):
        if PRIVATE_KEY_BLOCK.search(data.decode("latin-1")):
            found.append(("key", f"{what}: PRIVATE KEY block"))
    if b"kty" in data:
        for _, kind_found, detail in _jwk_objects(data.decode("latin-1")):
            found.append((kind_found, f"{what}: {detail}" if kind_found == "key" else detail))
    for _, pem in tlslib.certificates_in_text(data.decode("latin-1")) if CERT_MARKER.search(data) else []:
        found.append(("cert", pem))
    if not found:
        for kind_found, detail in _der_objects(data):
            found.append((kind_found, f"{what}: {detail}" if kind_found == "key" else detail))
    if not found:
        found += _inner_der_certs(data)
    return found


def _base64_blobs(text: str) -> Iterator[tuple[int, str]]:
    """Base64 values, including ones wrapped over several lines (a Secret's data)."""
    blob, start, last_full = "", 0, False
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        # A wrapped value goes on while the lines are pure base64; a short last
        # line belongs to it only after a full one, and padding ends it.
        if blob and not blob.endswith("=") and BASE64_LINE.match(stripped) and (len(stripped) >= 40 or last_full):
            blob += stripped
            last_full = len(stripped) >= 40
            continue
        if blob:
            yield start, blob
            blob = ""
        # The last base64 run on the line, whatever follows it: a value in quotes,
        # after a colon or an equals sign, or a Java constant ending in ";".
        tokens = BASE64_RUN.findall(stripped)
        if tokens and BASE64_TOKEN.match(tokens[-1]):
            blob, start, last_full = tokens[-1], number, len(tokens[-1]) >= 40
    if blob:
        yield start, blob


MAX_DEPTH = 3                   # archives and compressed files inside each other, opened this deep
NESTED_NOT_OPENED = (".jar", ".war", ".ear")      # a library's own jar: listed, not opened
COMPRESSED = ((b"\x1f\x8b", "gzip"), (b"BZh", "bzip2"), (b"\xfd7zXZ\x00", "xz"))


def _decompress(data: bytes, where: str) -> tuple[str, bytes] | None:
    """(format, the decompressed bytes) for a gzip, bzip2 or xz blob, else None.
    Bounded: what does not fit in MAX_BYTES is listed as not read in full."""
    kind = next((name for magic, name in COMPRESSED if data.startswith(magic)), None)
    if not kind:
        return None
    try:
        if kind == "gzip":
            engine = zlib.decompressobj(16 + zlib.MAX_WBITS)
            out = engine.decompress(data, MAX_BYTES)
            complete = not engine.unconsumed_tail
        elif kind == "bzip2":
            engine = bz2.BZ2Decompressor()
            out = engine.decompress(data, MAX_BYTES)
            complete = engine.eof or engine.needs_input
        else:
            engine = lzma.LZMADecompressor()
            out = engine.decompress(data, MAX_BYTES)
            complete = engine.eof or engine.needs_input
    except (zlib.error, OSError, EOFError, lzma.LZMAError, ValueError):
        note_skip(where, f"a {kind} file that could not be decompressed: it could hold a key", blocking=True)
        return None
    if not complete:
        note_skip(where, f"a {kind} file larger than {MAX_BYTES // 1_000_000} MB once decompressed: not read in full",
                  blocking=True)
    return kind, out


def _is_tar(name: str, data: bytes) -> bool:
    return name.lower().endswith((".tar", ".tgz", ".tar.gz", ".tar.bz2", ".tar.xz")) or data[257:262] == b"ustar"


def _archive_objects(path: Path | str, data: bytes, depth: int = 0) -> list[tuple[str, int, Any]]:
    """Keys, key stores and certificates in a zip or tar: every member, whatever
    it is called. A member that cannot be read (a password-protected one
    included) could hold a key, so it is listed as blocking."""
    found: list[tuple[str, int, Any]] = []
    where = str(path)

    def member(name: str, size: int, read) -> None:  # noqa: ANN001
        base = name.rsplit("/", 1)[-1].lower()
        if any(fnmatch.fnmatch(base, glob) for glob in KEY_FILE_GLOBS):
            found.append(("key", 0, f"archive member {name}: key or key-store file name"))
            return
        if base.endswith(NESTED_NOT_OPENED):
            return
        if size > MAX_BYTES:
            note_skip(f"{where}!{name}", f"an archive member larger than {MAX_BYTES // 1_000_000} MB: not read", blocking=True)
            return
        try:
            content = read()
        except Exception:  # noqa: BLE001 - an unreadable member is reported, never skipped silently
            note_skip(f"{where}!{name}", "an archive member that could not be read: it could hold a key", blocking=True)
            return
        found.extend((kind, 0, f"archive member {name}: {detail}" if kind == "key" else detail)
                     for kind, _, detail in _objects_in(content, base, f"{where}!{name}", depth + 1))

    try:
        if data[:4] == b"PK\x03\x04":
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                infos = archive.infolist()
                nested = sum(1 for info in infos if info.filename.lower().endswith(NESTED_NOT_OPENED))
                if nested:
                    note_skip(where, f"{nested} library archive(s) (.jar, .war, .ear) inside this archive were not opened")
                for info in infos:
                    if info.is_dir():
                        continue
                    if info.flag_bits & 0x1:
                        note_skip(f"{where}!{info.filename}", "a password-protected archive member: it cannot be read and "
                                  "could hold a key", blocking=True)
                        continue
                    member(info.filename, info.file_size, lambda info=info: archive.read(info))
        else:
            with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                for info in archive.getmembers():
                    if info.isfile():
                        member(info.name, info.size, lambda info=info: archive.extractfile(info).read())
    except (zipfile.BadZipFile, tarfile.TarError, OSError, RuntimeError, EOFError, zlib.error, lzma.LZMAError):
        note_skip(where, "an archive that could not be opened", blocking=True)
    return found


RECORD_FILE = re.compile(r"(^|/)tls-migration/(evidence|verification)/[^!]*\.(json|log|md|txt)$")


def _text_objects(text: str, name: str, where: str = "") -> list[tuple[str, int, Any]]:
    """Keys and certificates in a text: PEM blocks, base64 values (wrapped or
    not, a Java constant ending in ";" included), and, outside documentation
    and comments, the bare PRIVATE KEY marker (a key put together from string
    pieces in code)."""
    found: list[tuple[str, int, Any]] = []
    block = PRIVATE_KEY_BLOCK.search(text)
    if block:
        found.append(("key", text.count("\n", 0, block.start()) + 1, "PRIVATE KEY block"))
        end = text.find("-----END", block.start())
        end = text.find("\n", end) if end >= 0 else -1
        public = public_of_key(text[block.start():end if end >= 0 else len(text)].replace("\\n", "\n").encode())
        if public:
            found.append(("public", 0, public))
    elif not DOC_FILE.search(name) and not RECORD_FILE.search(where):
        # The run's own records (evidence, verification) may describe the marker; a block with a body there still fails.
        spans = None
        for marker in TEXT_KEY_MARKER.finditer(text):
            spans = spans or comment_spans(text, name)
            if not in_comment(spans, marker.start()):
                found.append(("key", text.count("\n", 0, marker.start()) + 1, BARE_MARKER))
                break
    for start, pem in tlslib.certificates_in_text(text):
        found.append(("cert", text.count("\n", 0, start) + 1, pem))
    for start, kind, detail in _jwk_objects(text):
        found.append((kind, text.count("\n", 0, start) + 1 if kind == "key" else 0, detail))
    tried = 0
    for number, blob in _base64_blobs(text):
        if len(blob) < 40:
            continue
        try:
            decoded = base64.b64decode(blob + "=" * (-len(blob) % 4), validate=False)
        except (binascii.Error, ValueError):
            continue
        if not (_looks_der(decoded) or tlslib._leading_der(decoded) or b"-----BEGIN" in decoded[:4096]  # noqa: SLF001
                or _store_kind(decoded[:16]) or KEY_MARKER.search(decoded) or b"kty" in decoded[:4096]):
            continue
        tried += 1
        if tried > 60:
            found.append(("unread", number, "more than 60 base64 values that look like certificates or keys: the rest were not decoded"))
            break
        for kind, detail in _binary_objects(decoded, "base64 value"):
            found.append((kind, number, detail))
    return found


BARE_MARKER = "PRIVATE KEY marker in code or config (a key put together from pieces)"
TEXT_KEY_MARKER = re.compile(r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----")


def _objects_in(data: bytes, name: str, where: str, depth: int = 0, text: str | None = None) -> list[tuple[str, int, Any]]:
    """Every key, key store and certificate in a blob: text, binary, compressed
    (gzip, bzip2, xz) or an archive, opened up to MAX_DEPTH levels deep."""
    if text is None:
        text = decode_text(data)
    if text is not None:
        found = _text_objects(text, name, where)
        for kind, _, detail in [item for item in found if item[0] == "unread"]:
            note_skip(where, detail, blocking=True)
        return [item for item in found if item[0] != "unread"]
    if depth > MAX_DEPTH:
        note_skip(where, f"nested more than {MAX_DEPTH} archives or compressed files deep: not opened", blocking=True)
        return []
    if data[:4] == b"PK\x03\x04" or _is_tar(name, data):
        return _archive_objects(where, data, depth)
    unpacked = _decompress(data, where)
    if unpacked:
        kind, inner = unpacked
        inner_name = re.sub(r"\.(gz|tgz|bz2|xz)$", "", name)
        return [(k, line, f"{kind}-compressed: {detail}" if k == "key" else detail)
                for k, line, detail in _objects_in(inner, inner_name, where + "!", depth + 1)]
    found = [(kind, 0, detail) for kind, detail in _binary_objects(data, "binary file")]
    for _, _, detail in [item for item in found if item[0] == "unread"]:
        note_skip(where, detail, blocking=True)
    return [item for item in found if item[0] != "unread"]


def embedded_objects(path: Path) -> list[tuple[str, int, Any]]:
    """Every key, key store and certificate in one file, whatever it is called
    and however it is encoded: ("key", line, reason) or ("cert", line, pem)."""
    key = str(path)
    if key in _OBJECT_CACHE:
        return _OBJECT_CACHE[key]
    found: list[tuple[str, int, Any]] = []
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    if size > MAX_BYTES:
        # Too large to hold in memory: searched in pieces for key markers only.
        try:
            with open(path, "rb") as handle:
                tail = b""
                while True:
                    chunk = handle.read(4_000_000)
                    if not chunk:
                        break
                    if KEY_MARKER.search(tail + chunk):
                        found.append(("key", 0, "PRIVATE KEY marker in a large file"))
                        break
                    tail = chunk[-64:]
        except OSError:
            note_skip(key, "could not be read", blocking=True)
        _OBJECT_CACHE[key] = found
        return found
    try:
        data = path.read_bytes()
    except OSError:
        note_skip(key, "could not be read", blocking=True)
        _OBJECT_CACHE[key] = found
        return found
    found = _objects_in(data, path.name, key, 0, read_text(path))
    _OBJECT_CACHE[key] = found
    return found


DEPENDENCY_DIRS = {"node_modules", ".venv", "venv", ".tox", "site-packages", "vendor", ".m2", ".gradle", ".npm", ".yarn"}
_INSTALL_MARKERS = {
    "node_modules": {"package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"},
    ".npm": {"package.json", "package-lock.json"},
    ".yarn": {"package.json", "yarn.lock"},
    ".venv": {"requirements.txt", "pyproject.toml", "Pipfile", "poetry.lock", "setup.py", "tox.ini"},
    "venv": {"requirements.txt", "pyproject.toml", "Pipfile", "poetry.lock", "setup.py", "tox.ini"},
    ".tox": {"tox.ini", "pyproject.toml", "setup.cfg"},
    "vendor": VENDOR_MARKERS,
    ".m2": {"pom.xml", "mvnw"},
    ".gradle": {"build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts", "gradlew"},
}


def dependency_install(repo: Path, path: Path) -> str | None:
    """The dependency folder a file sits in, when that folder is a recognisable
    install: the package manifest or lock file that fills it is beside it (or,
    for a Python environment, its pyvenv.cfg is inside). Otherwise None: a
    folder merely called node_modules or vendor is an ordinary folder."""
    try:
        parts = path.relative_to(repo.resolve()).parts
    except ValueError:
        return None
    for index, part in enumerate(parts[:-1]):
        if part not in DEPENDENCY_DIRS:
            continue
        folder = repo.resolve().joinpath(*parts[:index + 1])
        try:
            beside = set(os.listdir(folder.parent))
        except OSError:
            beside = set()
        if part == "site-packages":
            known = any((ancestor / "pyvenv.cfg").is_file() for ancestor in folder.parents)
        else:
            known = bool(beside & _INSTALL_MARKERS.get(part, set())) or (folder / "pyvenv.cfg").is_file()
        return "/".join(parts[:index + 1]) if known else None      # the outermost dependency folder decides
    return None


_PLANNED_CACHE: dict[str, set[str]] = {}


def planned_public_keys(repo: Path) -> set[str]:
    """Public keys of every certificate the migration planned or the toolkit made,
    from the public files in the repository: everything under tls-migration/
    (local certificates, kits, exported certificates) and every file a
    certificate plan there names."""
    key = str(repo)
    if key in _PLANNED_CACHE:
        return _PLANNED_CACHE[key]
    working = repo / WORKING_DIR
    files: set[Path] = set()
    if working.is_dir():
        for path in working.rglob("*"):
            if path.is_file() and path.suffix.lower() in (".crt", ".pem", ".cer"):
                files.add(path)
            elif path.is_file() and path.name.startswith("certs-to-check") and path.suffix in (".yaml", ".yml"):
                for name in re.findall(r"(?m)^[ \t]*(?:-\s*)?(?:path|issuer_ca)\s*:\s*[\"']?([^\s\"'#]+)", path.read_text(errors="replace")):
                    files.add(Path(os.path.expanduser(name)) if os.path.isabs(os.path.expanduser(name)) else repo / name)
    found: set[str] = set()
    for path in sorted(files):
        try:
            pems = [pem for _, pem in tlslib.certificates_in_text(path.read_text(errors="replace"))]
        except OSError:
            continue
        for pem in pems:
            public = public_of_cert(pem)
            if public:
                found.add(public)
    _PLANNED_CACHE[key] = found
    return found


def find_private_keys(repo: Path) -> list[dict[str, Any]]:
    """Key files, key blocks, key stores and encoded keys anywhere in the tree.
    Fail-closed: only the repository's own .git is left out, and a key store
    that cannot be opened to show it holds certificates only counts as a key
    store.

    Each hit has a severity. "fail" everywhere, except for a key inside a
    recognisable dependency install (node_modules beside package.json, a Python
    environment, vendored modules, a build tool's cache): third-party packages
    ship test keys. Such a key is "review", listed with its path, unless its
    public key is one the migration planned or the toolkit made (then it is
    this project's key, hidden among the dependencies) or it cannot be
    compared at all (encrypted): both fail."""
    found = []
    for path in iter_files(repo, purpose="keys"):
        name = path.name
        relative = rel(repo, path)
        named = any(fnmatch.fnmatch(name.lower(), glob) for glob in KEY_FILE_GLOBS)
        objects = embedded_objects(path)
        keys = [(line, detail) for kind, line, detail in objects if kind == "key"]
        install = dependency_install(repo, path) if (keys or named) else None
        if keys:
            line, detail = keys[0]
            severity = "fail"
            if install:
                planned = planned_public_keys(repo)
                publics = {value for kind, _, value in objects if kind == "public"}
                publics |= {p for p in (public_of_cert(value) for kind, _, value in objects if kind == "cert") if p}
                if publics & planned:
                    detail += f"; inside the dependency folder {install}, and it is the key of a certificate this migration planned"
                elif all(BARE_MARKER in d for _, d in keys):
                    # A library that reads keys names the marker in its code: there is no key material to compare.
                    severity = "review"
                    detail += f"; inside the dependency install {install}: the marker alone, no key material"
                elif not publics:
                    # An encrypted key (or a store that will not open) cannot be compared
                    # with the planned certificates: it could be this project's own key.
                    detail += (f"; inside the dependency install {install}, but it cannot be opened to compare with the "
                               "planned certificates (encrypted, or a store with an unknown password), so it is not let through")
                else:
                    severity = "review"
                    detail += f"; inside the dependency install {install}, and not the key of any planned certificate"
            found.append({"file": relative, "line": line, "reason": detail, "severity": severity})
            continue
        if named:
            certs_only = any(kind == "cert" for kind, _, _ in objects)
            try:
                head = path.read_bytes()[:16]
            except OSError:
                head = b""
            if certs_only and _store_kind(head):
                continue                       # a trust store: opened, certificates only
            text = read_text(path)
            if text is not None and re.search(r"-----BEGIN (?:CERTIFICATE|PUBLIC KEY)-----", text) and not KEY_MARKER.search(text.encode("latin-1", "replace")):
                continue                       # a public key or certificate that happens to be called *.key
            found.append({"file": relative, "line": 0, "reason": "key or key-store file name"
                          + (f"; inside the dependency install {install}, with nothing in it this reader takes for a key" if install else ""),
                          "severity": "review" if install else "fail"})
    return found


def find_ai_directed_text(repo: Path) -> list[dict[str, Any]]:
    found = []
    for path in iter_files(repo):
        text = read_text(path)
        if text is None:
            continue
        for match in AI_DIRECTED.finditer(text):
            number = text.count("\n", 0, match.start()) + 1
            found.append({"file": rel(repo, path), "line": number, "text": text.splitlines()[number - 1].strip()[:200]})
    return found


LOCAL_ALLOWED = (
    re.compile(r"(^|/)tls-migration/local/"),
    re.compile(r"(^|/)application-local\.(ya?ml|properties)$"),
    # A compose file is local-only when its name says so; any other may deploy a shared environment.
    re.compile(r"(^|/)docker-compose[^/]*\.local(?:\.[^/]*)?\.ya?ml$"),
    re.compile(r"(^|/)compose\.local(?:\.[^/]*)?\.ya?ml$"),
    re.compile(r"(^|/)\.env\.local$"),
)


def find_local_dev_refs(repo: Path, fingerprints: set[str], local_run: bool = False) -> list[dict[str, Any]]:
    """local-dev CAs outside local-only files: by name, by fingerprint, and by
    parsing every certificate found: PEM under any label a TLS library reads
    (CERTIFICATE, X509 CERTIFICATE, TRUSTED CERTIFICATE), base64 (wrapped or
    not), DER under any name, inside a trust store or an archive. Build output
    (target/, a jar) is read too: it is what ships. Dependency caches, nested
    .git folders and installed skills are not.
    In a local run, kits built for local consumers are local-only too."""
    found = []
    allowed = LOCAL_ALLOWED + ((re.compile(r"(^|/)tls-migration/kits/"),) if local_run else ())
    fingerprints = {fp for fp in fingerprints if len(fp) == 64}
    for path in iter_files(repo, purpose="certs"):
        relative = rel(repo, path)
        if any(p.search(relative) for p in allowed):
            continue
        text = read_text(path)
        if text is not None:
            for number, line in enumerate(text.splitlines(), 1):
                lowered = line.lower()
                if LOCAL_DEV.search(line) or any(fp in lowered or fp in lowered.replace(":", "") for fp in fingerprints):
                    found.append({"file": relative, "line": number, "text": line.strip()[:200]})
        for kind, number, pem in embedded_objects(path):
            if kind != "cert":
                continue
            try:
                info = tlslib.cert_info_from_pem(pem)
            except ValueError:
                continue
            names = [str(info.get("subject_cn") or ""), str(info.get("issuer_cn") or "")]
            if any(n.startswith("local-dev-") for n in names) or info.get("fingerprint_sha256") in fingerprints:
                found.append({"file": relative, "line": number,
                              "text": f"certificate subject {names[0]}, issuer {names[1]} is a local-dev CA or signed by one"})
    return found
