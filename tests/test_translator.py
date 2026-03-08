"""Unit tests for the translator module."""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from translator import generate_slug, translate, write_translated_file


class TestGenerateSlug(unittest.TestCase):
    def test_basic_slug(self):
        self.assertEqual(generate_slug("Hello World"), "hello-world")

    def test_special_characters(self):
        self.assertEqual(generate_slug("What's New in v2.0?"), "what-s-new-in-v2-0")

    def test_strips_leading_trailing_hyphens(self):
        slug = generate_slug("---test---")
        self.assertFalse(slug.startswith("-"))
        self.assertFalse(slug.endswith("-"))

    def test_collapses_multiple_hyphens(self):
        slug = generate_slug("a   b   c")
        self.assertNotIn("--", slug)
        self.assertEqual(slug, "a-b-c")

    def test_empty_after_strip(self):
        # Unicode-only title produces empty slug
        slug = generate_slug("")
        self.assertEqual(slug, "")


class TestWriteTranslatedFile(unittest.TestCase):
    def test_writes_file_with_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"output": {"tips_dir": tmpdir}}
            filepath = write_translated_file(
                title="测试标题",
                translated_content="这是翻译后的内容。",
                source_url="https://example.com/original",
                date_str="2026-03-08",
                config=config,
            )

            self.assertTrue(os.path.exists(filepath))
            self.assertIn("2026-03-08", os.path.basename(filepath))

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("---", content)
            self.assertIn('title: "测试标题"', content)
            self.assertIn("date: 2026-03-08", content)
            self.assertIn('original_url: "https://example.com/original"', content)
            self.assertIn("查看原文", content)
            self.assertIn("这是翻译后的内容。", content)

    def test_file_naming_convention(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"output": {"tips_dir": tmpdir}}
            filepath = write_translated_file(
                title="Performance Tuning Tips",
                translated_content="内容",
                source_url="https://example.com",
                date_str="2026-03-08",
                config=config,
            )
            basename = os.path.basename(filepath)
            self.assertEqual(basename, "2026-03-08-performance-tuning-tips.md")


class TestTranslate(unittest.TestCase):
    @patch("translator.call_gemini")
    def test_primary_success(self, mock_gemini):
        mock_gemini.return_value = "# 翻译标题\n\n翻译内容"
        config = {
            "llm": {
                "primary": {"provider": "gemini"},
                "fallback": {"provider": "deepseek"},
            }
        }
        result = translate("# Title\n\nContent", config)
        self.assertEqual(result, "# 翻译标题\n\n翻译内容")
        mock_gemini.assert_called_once()

    @patch("translator.call_deepseek")
    @patch("translator.call_gemini")
    def test_fallback_on_primary_failure(self, mock_gemini, mock_deepseek):
        mock_gemini.side_effect = RuntimeError("Gemini error")
        mock_deepseek.return_value = "# 备用翻译\n\n内容"
        config = {
            "llm": {
                "primary": {"provider": "gemini"},
                "fallback": {"provider": "deepseek"},
            }
        }
        result = translate("# Title\n\nContent", config)
        self.assertEqual(result, "# 备用翻译\n\n内容")
        mock_gemini.assert_called_once()
        mock_deepseek.assert_called_once()

    @patch("translator.call_deepseek")
    @patch("translator.call_gemini")
    def test_raises_when_both_fail(self, mock_gemini, mock_deepseek):
        mock_gemini.side_effect = RuntimeError("Gemini error")
        mock_deepseek.side_effect = RuntimeError("DeepSeek error")
        config = {
            "llm": {
                "primary": {"provider": "gemini"},
                "fallback": {"provider": "deepseek"},
            }
        }
        with self.assertRaises(RuntimeError) as ctx:
            translate("# Title\n\nContent", config)
        self.assertIn("All translation backends failed", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
