"""Notification sinks for alerter-generated events."""

from __future__ import annotations

import json
import smtplib
from email.mime.text import MIMEText
from typing import Callable, List, Optional


AlertHandler = Callable[[str, dict], None]


def console_notifier(*, prefix: str = "[ALERT]") -> AlertHandler:
    """Return a handler that prints alerts to stdout."""

    def handler(rule_name: str, entry: dict) -> None:
        ts = entry.get("timestamp", "?")
        msg = entry.get("message", "")
        print(f"{prefix} rule={rule_name!r} ts={ts} msg={msg!r}")

    return handler


def collecting_notifier(store: List[dict]) -> AlertHandler:
    """Return a handler that appends alert records to *store*.

    Useful for testing or in-process aggregation.
    """

    def handler(rule_name: str, entry: dict) -> None:
        store.append({"rule": rule_name, "entry": entry})

    return handler


def json_notifier(fp) -> AlertHandler:
    """Return a handler that writes JSON alert records to a file-like object."""

    def handler(rule_name: str, entry: dict) -> None:
        record = {"rule": rule_name, "entry": entry}
        fp.write(json.dumps(record) + "\n")

    return handler


def smtp_notifier(
    *,
    host: str,
    port: int = 25,
    from_addr: str,
    to_addrs: List[str],
    subject_prefix: str = "[logslice alert]",
    username: Optional[str] = None,
    password: Optional[str] = None,
    use_tls: bool = False,
) -> AlertHandler:
    """Return a handler that sends an e-mail for every alert.

    Raises ``smtplib.SMTPException`` on delivery failure.
    """

    def handler(rule_name: str, entry: dict) -> None:
        subject = f"{subject_prefix} {rule_name}"
        body = json.dumps(entry, indent=2, default=str)
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = ", ".join(to_addrs)

        cls = smtplib.SMTP_SSL if use_tls else smtplib.SMTP
        with cls(host, port) as smtp:
            if username and password:
                smtp.login(username, password)
            smtp.sendmail(from_addr, to_addrs, msg.as_string())

    return handler


def multi_notifier(*handlers: AlertHandler) -> AlertHandler:
    """Combine several handlers into one; all are called for every alert."""

    def handler(rule_name: str, entry: dict) -> None:
        for h in handlers:
            h(rule_name, entry)

    return handler
