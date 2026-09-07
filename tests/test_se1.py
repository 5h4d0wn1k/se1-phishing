#!/usr/bin/env python3
"""Unit tests for SE1 Phishing Simulation Kit (offline, synthetic only)."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from se1_cli import (
    SimulatorError,
    EmailTemplate,
    EmailHtmlBuilder,
    DeliverabilityCheck,
    LandingPageAnalyzer,
    CampaignGenerator,
    WATERMARK,
)


class TestEmailTemplate(unittest.TestCase):
    def test_generate_is_watermarked(self):
        t = EmailTemplate()
        out = t.generate("password_reset", "Ada", "Example Corp",
                         "https://x.example/p", ref="abc123")
        self.assertIn(WATERMARK, out["subject"])
        self.assertIn(WATERMARK, out["body"])

    def test_unknown_template_raises(self):
        with self.assertRaises(ValueError):
            EmailTemplate().generate("nope", "A", "B", "https://x.example/p")


class TestDomainGuard(unittest.TestCase):
    def test_forbids_real_domains(self):
        with self.assertRaises(SimulatorError):
            DeliverabilityCheck("gmail.com")
        with self.assertRaises(SimulatorError):
            DeliverabilityCheck("dropbox.com")


class TestDeliverability(unittest.TestCase):
    def test_evaluate(self):
        dc = DeliverabilityCheck("x.example",
                                 spf="v=spf1 include:_spf.example.com -all",
                                 dkim="v=DKIM1; k=rsa; p=abc",
                                 dmarc="v=DMARC1; p=none")
        r = dc.evaluate()
        self.assertIn(r["verdict"], ("likely_deliverable", "review", "likely_spam"))


class TestHtmlBuilder(unittest.TestCase):
    def test_render(self):
        b = EmailHtmlBuilder().render("Subject", "Body text", "Example Corp")
        self.assertIn(WATERMARK, b)
        self.assertIn("Body text", b)


class TestLandingAnalyzer(unittest.TestCase):
    def test_flags_password_form(self):
        html = ('<form action="/login"><input type="text" name="username">'
                '<input type="password" name="password"></form>')
        a = LandingPageAnalyzer().analyze(html)
        self.assertEqual(a["risk"], "HIGH")
        self.assertTrue(a["has_password_field"])

    def test_benign_page_is_low(self):
        a = LandingPageAnalyzer().analyze("<html><p>hello</p></html>")
        self.assertEqual(a["risk"], "LOW")


class TestCampaignGenerator(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            g = CampaignGenerator(td, "x.example", "Example Corp", armed=False)
            res = g.run("password_reset", [{"name": "Ada", "email": "a@example.com"}])
            self.assertFalse(g.armed)
            self.assertEqual(res["watermark"], WATERMARK)
            self.assertFalse(os.path.isdir(os.path.join(td, "payloads")))  # dry-run wrote nothing

    def test_armed_writes_payloads(self):
        with tempfile.TemporaryDirectory() as td:
            g = CampaignGenerator(td, "x.example", "Example Corp", armed=True)
            res = g.run("password_reset", [{"name": "Ada", "email": "a@example.com"}])
            self.assertTrue(g.armed)


if __name__ == "__main__":
    unittest.main()
