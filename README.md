# SE1 — Phishing Simulation Kit

Local, watermarked phishing **campaign simulator** for AUTHORIZED internal security
training. Everything runs against synthetic personas, `example.com` addresses and
`.example` / `.test` / `.internal` domains. Dry-run by default; real artifact
writing requires `--armed` AND a local `--lab-root`. Real-world domains are
refused outright.

## Features

- **Email template generator** — password-reset / account-verify templates, every
  artifact watermarked `SIMULATION / AUTHORIZED TRAINING ONLY`.
- **HTML email builder** — watermarked `.html` render for local inspection.
- **Deliverability scoring** — structural SPF / DKIM / DMARC scoring for **your own**
  `.example` domain.
- **Landing-page analyzer (defensive)** — flags credential-harvesting indicators
  (password fields, login forms, CVV/SSN keywords) so defenders can recognize them.
- **Dry-run default** — writes nothing until `--armed` is passed.

## IMPORTANT: Read before use.

**This is a DEFENSIVE / EDUCATIONAL tool with hard consent gating.**
This project is provided for **educational and authorized security testing
purposes only**. Running this tool against any target without explicit,
written, pre-approved consent from that target's organization is strictly
prohibited and may violate applicable law.

### Authorization Requirements
- You MUST have explicit written permission from the owning organization before
  any simulated campaign.
- This kit is a **LOCAL generator** for internal simulation. It refuses real
  domains, high-traffic domains, and any real personal data.
- `--target-org` is locked to `OWN` in lab mode; real-mode would require multiple
  additional explicit flags (not provided here).

### Anti-Abuse Safeguards
- `lab-mode` is **ON** by default; every run requires an explicit `--lab-root`.
- `--armed` is **off** by default (dry-run). Artifacts are only written under the
  lab root.
- Domain validation refuses everything except `.example`, `.test`, `.internal`,
  `.invalid`.
- All templates and payloads carry the watermark
  "SIMULATION / AUTHORIZED TRAINING ONLY".
- No real personal data is accepted; the CLI uses only synthetic personas.

### Legal Framework
- **Computer Fraud and Abuse Act (CFAA)** (18 U.S.C. § 1030): unauthorized access
  is a federal crime.
- **Wiretap Act (18 U.S.C. § 2511)** and state wiretapping statutes: interception
  without consent is illegal.
- **GDPR/CCPA**: data collection may be subject to privacy regulations.
- Attempts to remove these safeguards will be refused.

### Prohibited Use
- Sending simulated emails to real people or real domains.
- Attempting to intercept or collect credentials from anyone.
- Any activity that violates applicable laws or regulations.

### No Warranty
This software is provided "AS IS" without warranty of any kind. The author is not
responsible for misuse or damage.

### Responsible Disclosure
Report discovered vulnerabilities privately to the vendor/owner, allow reasonable
time for remediation, and do not exploit beyond proof of concept.

## Live Lab Test Plan

1. `python3 se1_cli.py --lab-root ./lab --demo` → exit 0, dry-run output on stdout.
2. `python3 se1_cli.py --lab-root ./lab --demo --armed` → writes watermarked
   payloads under `./lab/payloads/`.
3. `python3 se1_cli.py --lab-root ./lab --demo --deliverability` → prints scores.
4. `python3 se1_cli.py --help` → usage and required `--lab-root`.
5. Negative: `python3 se1_cli.py --lab-root ./lab --target-org EvilCorp` must exit
   non-zero with a refusal message.
6. `python -m unittest discover -s tests` → all tests pass offline.

## Metrics

- Campaign ids: 6-char random refs.
- Targets in demo: 3 synthetic personas (example.com).
- Test count: 8 (see `tests/test_se1.py`).
- Deliverability verdicts: `likely_deliverable` / `review` / `likely_spam`.
- Landing analyzer risk ratings: LOW / MEDIUM / HIGH.

## Usage

```bash
# dry-run demo (safe default)
python3 se1_cli.py --lab-root ./lab --demo

# local artifact build (still fully synthetic + watermarked)
python3 se1_cli.py --lab-root ./lab --demo --armed

# deliverability scoring for your OWN .example domain
python3 se1_cli.py --lab-root ./lab --deliverability

# defensive landing-page analysis
python3 se1_cli.py --lab-root ./lab --analyze-landing page.html
```

## License

MIT