#!/usr/bin/env python3
"""
PreToolUse guard hook for Claude Code (Bash matcher).

Claude Code permission rules in settings.json match command TEXT, not meaning —
they can't tell `psql -c "SELECT ..."` (read) from `psql -c "DELETE ..."` (write).
This hook inspects each Bash command and DENIES the few things that need content
awareness, then stays silent so the normal allow/deny rules handle everything else.

It enforces three policies for Claude (NOT for the app — the running server's own
SQLAlchemy writes are untouched; this only sees Bash commands):

  1. DB is read-only  — block writes/DDL via psql/pgcli/pg_restore, and `dropdb`.
  2. Network is local  — block curl/wget to any host other than localhost.
  3. Data is protected — block `docker compose down -v` and `docker volume rm`.

Contract: read JSON from stdin; to block, print a deny decision as JSON to stdout
and exit 0; to allow, print nothing and exit 0.

CAVEAT: the SQL check is a heuristic keyword match. It errs toward blocking (a
SELECT whose text literally contains "create"/"insert" is blocked — safe but a
false positive), and a write hidden inside a stored function could slip past. The
real guarantee is a read-only Postgres role; this hook is a guardrail, not a sandbox.
"""

import json
import re
import sys


def deny(reason: str) -> None:
    """Emit a PreToolUse deny decision and exit."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


# Word-boundary keywords for SQL writes/DDL. Word boundaries are deliberate: they
# do NOT match this app's own column names created_at / updated_at / deleted_at
# (the trailing "d"/"d_at" removes the boundary), so plain SELECTs pass.
WRITE_SQL = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|reindex|vacuum)\b",
    re.IGNORECASE,
)
COPY_FROM = re.compile(r"\bcopy\b.*\bfrom\b", re.IGNORECASE | re.DOTALL)

DB_CLI = re.compile(r"(^|[\s;&|()])(psql|pgcli|pg_restore)\b")
DROPDB = re.compile(r"(^|[\s;&|()])dropdb\b")

NET_CLI = re.compile(r"(^|[\s;&|()])(curl|wget)\b")
URL_HOST = re.compile(r"https?://([^/\s'\"]+)", re.IGNORECASE)
# bare host arg like example.com or 127.0.0.1[:port][/path] (must contain a dot)
BARE_HOST = re.compile(r"(?:^|\s)((?:[A-Za-z0-9-]+\.)+[A-Za-z0-9-]+(?::\d+)?(?:/\S*)?)")

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "[::1]", "0.0.0.0"}


def host_of(target: str) -> str:
    """Reduce a URL host / bare host[:port]/path to just the hostname."""
    target = target.split("@")[-1]  # strip user:pass@
    target = target.split("/")[0]  # strip /path
    if target.startswith("[") and "]" in target:  # [::1]:port
        return target[: target.index("]") + 1]
    return target.split(":")[0]  # strip :port


def is_local(target: str) -> bool:
    h = host_of(target)
    return h in LOCAL_HOSTS or h == "localhost" or h.endswith(".localhost")


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unparseable input -> don't interfere

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    cmd = (data.get("tool_input") or {}).get("command", "") or ""

    # --- 1. DB read-only -----------------------------------------------------
    if DROPDB.search(cmd):
        deny("DB is read-only for Claude: `dropdb` is blocked.")

    if DB_CLI.search(cmd):
        if WRITE_SQL.search(cmd) or COPY_FROM.search(cmd):
            deny(
                "DB is read-only for Claude: write/DDL statements "
                "(INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/CREATE/GRANT/…) are blocked. "
                "Run a SELECT, or perform the write yourself."
            )
        if re.search(r"(^|\s)(-f|--file)\b", cmd):
            deny(
                "DB is read-only for Claude: `psql -f <file>` runs SQL that can't be "
                "verified as read-only, so it is blocked."
            )
        has_command = re.search(r"(^|\s)(-c|--command)\b", cmd)
        has_read_list = re.search(r"(^|\s)(-l\b|-lqt\b|--list\b)", cmd)
        if not has_command and not has_read_list:
            deny(
                "DB is read-only for Claude: interactive psql can't be verified as "
                'read-only. Use psql -c "SELECT …" instead.'
            )

    # --- 2. Outbound network restricted to localhost ------------------------
    if NET_CLI.search(cmd):
        targets = URL_HOST.findall(cmd)
        if not targets:
            # No explicit URL: look for a bare domain-like target (example.com).
            # If there's none (e.g. `curl --version`), let it through.
            targets = [m for m in BARE_HOST.findall(cmd)]
        external = [t for t in targets if not is_local(t)]
        if external:
            deny(
                "Outbound network is restricted to localhost for Claude: external "
                f"curl/wget is blocked (target: {external[0]}). Only localhost/127.0.0.1 "
                "is allowed."
            )

    # --- 3. Protect persistent data -----------------------------------------
    low = cmd.lower()
    if re.search(r"docker\s+compose\s+down", low) and re.search(
        r"(^|\s)(-v\b|--volumes\b)", cmd
    ):
        deny(
            "Protected: `docker compose down -v` would wipe the Postgres data volume. "
            "Use `docker compose down` (without -v)."
        )
    if re.search(r"docker\s+volume\s+rm\b", low):
        deny("Protected: `docker volume rm` is blocked (it would delete persistent data).")

    sys.exit(0)  # no objection -> normal permission rules apply


if __name__ == "__main__":
    main()
