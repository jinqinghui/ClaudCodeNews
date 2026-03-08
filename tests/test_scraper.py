"""Unit tests for the scraper module."""

import hashlib
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from scraper import _html_to_markdown, _md5, fetch_web_source


class TestMd5(unittest.TestCase):
    def test_consistent_hash(self):
        text = "hello world"
        expected = hashlib.md5(text.encode("utf-8")).hexdigest()
        self.assertEqual(_md5(text), expected)

    def test_different_text_different_hash(self):
        self.assertNotEqual(_md5("hello"), _md5("world"))


class TestHtmlToMarkdown(unittest.TestCase):
    def test_extracts_headings(self):
        html = "<html><body><h1>Title</h1><p>Content here</p></body></html>"
        md = _html_to_markdown(html)
        self.assertIn("# Title", md)
        self.assertIn("Content here", md)

    def test_extracts_list_items(self):
        html = "<html><body><ul><li>Item one</li><li>Item two</li></ul></body></html>"
        md = _html_to_markdown(html)
        self.assertIn("- Item one", md)
        self.assertIn("- Item two", md)

    def test_extracts_code_blocks(self):
        html = "<html><body><pre>print('hello')</pre></body></html>"
        md = _html_to_markdown(html)
        self.assertIn("```", md)
        self.assertIn("print('hello')", md)

    def test_removes_script_tags(self):
        html = "<html><body><p>Visible</p><script>alert('xss')</script></body></html>"
        md = _html_to_markdown(html)
        self.assertIn("Visible", md)
        self.assertNotIn("alert", md)


class TestDeduplication(unittest.TestCase):
    @patch("scraper.requests.get")
    def test_skips_duplicate_content(self, mock_get):
        html = "<html><body><p>Existing content</p></body></html>"
        content_md = _html_to_markdown(html)
        content_hash = _md5(content_md)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        source = {"type": "web", "urls": ["https://example.com/doc"]}
        manifest = {
            "processed": {content_hash: {"source_url": "https://example.com/doc"}},
            "last_github_sha": {},
        }

        results = fetch_web_source(source, manifest)
        self.assertEqual(len(results), 0)

    @patch("scraper.requests.get")
    def test_processes_new_content(self, mock_get):
        html = "<html><title>New Doc</title><body><p>Brand new content</p></body></html>"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        source = {"type": "web", "urls": ["https://example.com/new"]}
        manifest = {"processed": {}, "last_github_sha": {}}

        results = fetch_web_source(source, manifest)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "New Doc")
        self.assertIn("Brand new content", results[0]["content_md"])
        self.assertEqual(results[0]["source_url"], "https://example.com/new")
        self.assertIn("fetched_at", results[0])

    @patch("scraper.requests.get")
    def test_continues_on_error(self, mock_get):
        import requests as req

        mock_get.side_effect = req.ConnectionError("Connection failed")

        source = {"type": "web", "urls": ["https://unreachable.example.com"]}
        manifest = {"processed": {}, "last_github_sha": {}}

        results = fetch_web_source(source, manifest)
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
