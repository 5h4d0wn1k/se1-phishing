> **⚠️ EDUCATIONAL USE ONLY — AUTHORIZED TESTING ONLY.**
> This project exists for education, research, and **defense of systems you own
> or hold explicit written authorization to assess**. Unauthorized use is
> prohibited and may be illegal. Read [ETHICS.md](ETHICS.md) and
> [SCOPE.md](SCOPE.md) before use. Use at your own risk; **AS IS**, no warranty.

# SE1 — Phishing Simulation Kit (Authorized Awareness Labs)

Local, watermarked phishing campaign simulator for authorized internal security training: synthetic personas, `.example`/`.test`/`.internal` domains only, dry-run by default, and artifact writing gated behind `--armed`.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/5h4d0wn1k/se1-phishing.svg)](https://github.com/5h4d0wn1k/se1-phishing)
[![Last commit](https://img.shields.io/github/last-commit/5h4d0wn1k/se1-phishing.svg)](https://github.com/5h4d0wn1k/se1-phishing)
[![Issues](https://img.shields.io/github/issues/5h4d0wn1k/se1-phishing.svg)](https://github.com/5h4d0wn1k/se1-phishing)

## Why

Phishing awareness works best with simulations — but simulations must never bleed into real abuse. SE1 is a consent-gated, locally run generator that produces watermarked `password-reset` / `account-verify` email templates and HTML renders against synthetic personas, scores email deliverability structure for **your own** `.example` domain, and analyzes landing pages for credential-harvesting indicators. Every artifact carries `SIMULATION / AUTHORIZED TRAINING ONLY`; real domains, high-traffic domains, and real personal data are refused outright.

## Features

- **Email template generator** — `--template password_reset|account_verify`, every artifact watermarked
- **HTML email builder** — watermarked `.html` render for local inspection
- **Deliverability scoring** — structural SPF / DKIM / DMARC evaluation for your own `.example` domain
- **Defensive landing-page analyzer** — flags credential-harvesting indicators (password fields, login forms, CVV/SSN keywords)
- **Dry-run by default** — writes nothing until `--armed` and a local `--lab-root`
- **Hard anti-abuse gates** — `.example`/`.test`/`.internal`/`.invalid` TLDs only; `--target-org` locked to `OWN`

## Quickstart

```bash
# Dry-run demo (safe default)
python3 se1_cli.py --lab-root ./lab --demo

# Local watermarked artifact build (synthetic personas only)
python3 se1_cli.py --lab-root ./lab --demo --armed

# Deliverability scoring for your own .example domain
python3 se1_cli.py --lab-root ./lab --deliverability

# Defensive landing-page indicator analysis
python3 se1_cli.py --lab-root ./lab --analyze-landing page.html

# Unit tests (8 offline tests)
python3 -m unittest discover -s tests
```

## Project structure

- `se1_cli.py` — CLI entry point; `phishing_framework.py` — generator, deliverability, analyzer
- `tests/` — offline unit tests over templates, gates and scoring

## Documentation

- [ETHICS.md](ETHICS.md) — educational purpose and authorized use only
- [SCOPE.md](SCOPE.md) — authorized-testing scope checklist
- [SECURITY.md](SECURITY.md) — vulnerability reporting
- [CONTRIBUTING.md](CONTRIBUTING.md) — safe contribution guidelines

## Contributing

New templates, indicator rules and gate tests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md); the kit must stay local, synthetic, and refusal-first.

## License

MIT — see [LICENSE](LICENSE). Provided **AS IS**, without warranty, for education and authorized security-awareness training only.