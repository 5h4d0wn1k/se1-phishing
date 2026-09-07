#!/usr/bin/env python3
"""
SE1 — Phishing Simulation Kit
Local phishing campaign simulator for AUTHORIZED internal security-training drills.

Anti-abuse by default:
  * lab-mode is ON; every run requires an explicit --lab-root
  * dry-run is default; real simulation requires --armed
  * refuses real-world domains and high-traffic domains
  * all artifacts watermarked "SIMULATION / AUTHORIZED TRAINING ONLY"
"""

import argparse
import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

WATERMARK = "SIMULATION / AUTHORIZED TRAINING ONLY"
ALLOWED_TLDS = {".example", ".internal", ".test", ".invalid"}
RFC5737_IPS = ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")
FORBIDDEN_KEYWORDS = ["password", "logon", "reset", "ssn", "cvv", "card"]
LANDING_INDICATORS = [
    "password",
    "username",
    "verify",
    "ssn",
    "credit card",
    "cvv",
    "bank",
    "login",
]


class SimulatorError(Exception):
    """Raised when a safety/dry-run constraint is violated."""


def _validate_domain(domain: str) -> None:
    """Block real / high-traffic / credential-harvesting domains."""
    d = domain.lower().strip()
    if not d.endswith(tuple(ALLOWED_TLDS)):
        raise SimulatorError(
            f"Refusing domain '{domain}': only {sorted(ALLOWED_TLDS)} are allowed in lab mode."
        )


def _watermark(text: str) -> str:
    return f"[{WATERMARK}]\n{text}"


def spf_score(record: str) -> int:
    """Score an SPF record for how convincingly it is structured (0-100)."""
    score = 0
    r = record.lower().strip()
    if r.startswith("v=spf1"):
        score += 30
    if " include:" in r:
        score += 25
    if " -all" in r:
        score += 15
    if " mx" in r or " a " in r:
        score += 15
    if "redirect=" in r:
        score += 10
    return min(100, score)


def dkim_score(record: str) -> int:
    """Score a DKIM record structurally (0-100)."""
    score = 0
    r = record.lower().strip()
    if " v=dkim1" in r or r.startswith("v=dkim1"):
        score += 30
    if " k=rsa" in r:
        score += 15
    if " p=" in r:
        score += 30
    if "s=email" in r:
        score += 15
    return min(100, score)


class EmailTemplate:
    """Local email template generator, watermarked & domain-safe."""

    def __init__(self):
        self.templates = {
            "password_reset": {
                "subject": "[SIM] Password Reset Request {ref}",
                "body": (
                    "Dear {name},\n\n"
                    "A request to reset your password for the {company} "
                    "training-domain account was received.\n\n"
                    "Visit: {url}\n\n"
                    "If you did not request this, contact internal security.\n"
                    "Best regards,\n{company} Security Team (drill)"
                ),
            },
            "account_verify": {
                "subject": "[SIM] Account Verification {ref}",
                "body": (
                    "Dear {name},\n\n"
                    "Your {company} training account requires verification "
                    "as part of an internal drill.\n\n"
                    "Visit: {url}\n\n"
                    "Thank you,\n{company} Support (drill)"
                ),
            },
        }

    def generate(self, template_type, name, company, url, ref=None):
        ref = ref or str(uuid.uuid4())[:6]
        if template_type not in self.templates:
            raise ValueError(f"Unknown template: {template_type}")
        body = self.templates[template_type]["body"].format(
            name=name, company=company, url=url, ref=ref
        )
        subject = self.templates[template_type]["subject"].format(ref=ref)
        return {
            "subject": _watermark(subject),
            "body": _watermark(body),
            "ref": ref,
        }

    def list_templates(self):
        return list(self.templates.keys())


class EmailHtmlBuilder:
    """Builds a watermarked, training-only HTML email."""

    def render(self, subject, body, company):
        safe = body.replace("\n", "<br>")
        return (
            f"<!DOCTYPE html><html><body>"
            f"<p style='color:#999;font-size:11px'>{WATERMARK}</p>"
            f"<h3>{subject}</h3><div>{safe}</div>"
            f"<hr><p style='color:#bbb'>{WATERMARK} — {company}</p>"
            f"</body></html>"
        )


class DeliverabilityCheck:
    """Checks deliverability for your OWN domain using provided fixture records."""

    def __init__(self, domain, spf=None, dkim=None, dmarc=None):
        _validate_domain(domain)
        self.domain = domain
        self.spf = spf or ""
        self.dkim = dkim or ""
        self.dmarc = dmarc or ""

    def evaluate(self):
        s = spf_score(self.spf)
        d = dkim_score(self.dkim)
        dm = dkim_score(self.dmarc) if self.dmarc else 0
        overall = round((s + d + dm) / 3)
        return {
            "domain": self.domain,
            "spf_score": s,
            "dkim_score": d,
            "dmarc_score": dm,
            "overall": overall,
            "verdict": (
                "likely_deliverable"
                if overall >= 60
                else "review"
                if overall >= 30
                else "likely_spam"
            ),
        }


class LandingPageAnalyzer:
    """Defensive analyzer that flags credential-harvesting indicators in a page."""

    def analyze(self, html):
        lowered = html.lower()
        found = [ind for ind in LANDING_INDICATORS if ind in lowered]
        has_form = "<form" in lowered and "</form>" in lowered
        has_password = "type=\"password\"" in lowered or "type='password'" in lowered
        return {
            "credential_indicators": found,
            "has_login_form": has_form,
            "has_password_field": has_password,
            "risk": "HIGH" if has_password and has_form else ("MEDIUM" if has_form else "LOW"),
            "watermarked": WATERMARK in html,
        }


class CampaignGenerator:
    """Local-only synthetic campaign generator (dry-run by default)."""

    def __init__(self, lab_root, domain, company, armed=False):
        self.lab_root = Path(lab_root)
        self.domain = domain
        self.company = company
        self.armed = armed
        _validate_domain(domain)
        if not self.armed:
            print("  [dry-run] no payloads written. Pass --armed to build artifacts locally.")

    def run(self, template_type, target_list, outdir="payloads"):
        tmpl = EmailTemplate()
        ref = str(uuid.uuid4())[:6]
        artifacts = []
        for t in target_list:
            url = f"https://{self.domain}/sim/{ref}"
            email = tmpl.generate(template_type, t["name"], self.company, url, ref)
            artifacts.append({
                "to": t.get("email"),
                "subject": email["subject"],
                "body": email["body"],
                "url": url,
                "watermarked": True,
            })
        result = {
            "campaign": ref,
            "domain": self.domain,
            "company": self.company,
            "created": datetime.now().isoformat(),
            "artifacts": artifacts,
            "watermark": WATERMARK,
        }
        if self.armed:
            out = self.lab_root / outdir
            out.mkdir(parents=True, exist_ok=True)
            for a in artifacts:
                safe = re.sub(r"[^a-z0-9]+", "_", a["to"].split("@")[0].lower())
                (out / f"{ref}_{safe}.txt").write_text(a["body"])
            print(f"  [armed] wrote {len(artifacts)} payload(s) to {out}/")
        return result


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="se1-phishing",
        description="Local phishing-campaign simulation kit (authorized training only).",
    )
    parser.add_argument("--lab-root", required=True, help="Local lab folder (required).")
    parser.add_argument("--target-org", default="OWN", help="Target org; default OWN.")
    parser.add_argument("--domain", default="sh4d0wn1k.example",
                        help="Your OWN simulation domain (example/ test TLDs only).")
    parser.add_argument("--company", default="Example Corp", help="Display company name.")
    parser.add_argument("--armed", action="store_true",
                        help="Allow writing payload artifacts to lab-root (dry-run by default).")
    parser.add_argument("--demo", action="store_true",
                        help="Run offline demo against synthetic personas.")
    parser.add_argument("--template", default="password_reset",
                        choices=["password_reset", "account_verify"])
    parser.add_argument("--deliverability", action="store_true",
                        help="Score SPF/DKIM/DMARC records for your own domain.")
    parser.add_argument("--analyze-landing", metavar="HTML_FILE",
                        help="Run defensive landing-page indicator analysis.")
    args = parser.parse_args(argv)

    lab = Path(args.lab_root)
    lab.mkdir(parents=True, exist_ok=True)
    if args.target_org != "OWN":
        raise SimulatorError("Only --target-org OWN is permitted in lab mode.")

    print(f"SE1 Phishing Simulation Kit [{WATERMARK}]")
    print("=" * 60)

    if args.deliverability:
        dc = DeliverabilityCheck(
            args.domain,
            spf="v=spf1 include:_spf.example.com -all",
            dkim="v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC",
        )
        print(json.dumps(dc.evaluate(), indent=2))
    else:
        gen = CampaignGenerator(lab, args.domain, args.company, armed=args.armed)
        targets = [
            {"name": "Ada Lovelace (VP)", "email": "ada.lovelace@example.com"},
            {"name": "Grace Hopper (CFO)", "email": "grace.hopper@example.com"},
            {"name": "Katherine Johnson (Eng)", "email": "kate.johnson@example.com"},
        ]
        res = gen.run(args.template, targets)
        print(f"\nCampaign {res['campaign']} prepared for {len(res['artifacts'])} synthetic targets.")
        print(f"Domain: {res['domain']} | Watermark embedded: yes")

    if args.analyze_landing:
        html = Path(args.analyze_landing).read_text()
        print(json.dumps(LandingPageAnalyzer().analyze(html), indent=2))

    print("\nDemo complete (offline, synthetic). Exit 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
