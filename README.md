# SE1 — Phishing Framework

Email template generation, credential capture server, landing page builder, tracking pixels.

## Overview

This project implements a phishing simulation framework that:
- Generates email templates for various attack scenarios
- Builds realistic landing pages for credential capture
- Tracks email opens via invisible pixels
- Captures and stores submitted credentials
- Orchestrates complete phishing campaigns

## Features

- **Email Templates**: Pre-built templates for password resets, account verification, invoices
- **Landing Pages**: Customizable HTML forms that mimic legitimate sites
- **Tracking Pixels**: 1x1 GIF pixels for tracking email opens
- **Credential Capture**: HTTP server for harvesting form submissions
- **Campaign Management**: Full campaign orchestration and statistics

## Installation

No external dependencies required — uses Python standard library only.

```bash
python3 phishing_framework.py
```

## Usage

### Generate Email Templates
```python
from phishing_framework import EmailTemplate

template = EmailTemplate()
email = template.generate(
    template_type="password_reset",
    name="John Doe",
    company="Example Corp",
    url="http://your-server.com/page"
)
```

### Build Landing Page
```python
from phishing_framework import LandingPageBuilder

builder = LandingPageBuilder()
html = builder.build_page(
    company="Example Corp",
    title="Login",
    fields=["username", "password"],
    action="http://your-server.com/capture"
)
```

### Start Capture Server
```python
from phishing_framework import PhishingCampaign

campaign = PhishingCampaign("http://localhost:8080")
campaign.start_server(port=8080)
```

### Run Campaign
```python
targets = [
    {"name": "John", "email": "john@example.com", "id": "001"},
    {"name": "Jane", "email": "jane@example.com", "id": "002"}
]

campaign = PhishingCampaign("http://localhost:8080")
result = campaign.create_campaign(
    name="Test Campaign",
    template_type="password_reset",
    target_company="Example Corp",
    target_list=targets,
    form_fields=["username", "password"]
)
```

## Example Output

```
SE1 — Phishing Framework
========================================

Available email templates:
  - password_reset
  - account_verify
  - invoice

Campaign created: a1b2c3d4
Landing page: landing_a1b2c3d4.html
Emails prepared: 2

[*] Phishing server running on port 8080
[14:30:15] ('192.168.1.100', 52341) "POST /capture HTTP/1.1" 302 -
[CAPTURED] ID: e5f6g7h8 from 192.168.1.100
```

## Legal Disclaimer

**IMPORTANT: Read before use.**

This project is provided for **educational and authorized security testing purposes only**. 

### Authorization Requirements
- You MUST have explicit written permission from the network owner before using this tool
- Unauthorized interception of network communications is illegal under federal and state laws
- This tool should ONLY be used on networks you own or have written authorization to test

### Legal Framework
- **Computer Fraud and Abuse Act (CFAA)**: Unauthorized access to computer systems is a federal crime
- **Wiretap Act (18 U.S.C. § 2511)**: Interception of electronic communications without consent is illegal
- **State Laws**: Many states have additional computer crime and wiretapping statutes
- **GDPR/CCPA**: Data collection may be subject to privacy regulations

### Acceptable Use
- Testing security of your own networks
- Authorized penetration testing with written scope
- Academic research in controlled lab environments
- Security education and training

### Prohibited Use
- Intercepting communications on networks you do not own
- Attacking infrastructure without authorization
- Any activity that violates applicable laws or regulations
- Commercial use without proper licensing

### No Warranty
This software is provided "AS IS" without warranty of any kind. The author is not responsible for any misuse or damage caused by this software.

### Responsible Disclosure
If you discover vulnerabilities using this tool, follow responsible disclosure practices:
1. Report to the vendor/owner privately
2. Allow reasonable time for remediation
3. Do not exploit beyond proof of concept

## License

MIT
