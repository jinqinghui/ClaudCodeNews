"""LLM translation module.

Translates English Markdown content to Chinese using Gemini (primary)
or DeepSeek (fallback) LLM backends. Preserves Markdown formatting,
code blocks, and inline code.
"""

import logging
import os
import re
import unicodedata
from datetime import datetime
from urllib.parse import urljoin

import requests
import yaml

logger = logging.getLogger(__name__)


def load_config(config_path=None):
    """Load configuration from config.yaml."""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def call_gemini(content, config):
    """Call Gemini API to translate content.

    Args:
        content: English Markdown content to translate.
        config: Full config dict (from config.yaml).

    Returns:
        Translated content string.

    Raises:
        RuntimeError: If the API call fails.
    """
    llm_cfg = config["llm"]["primary"]
    api_key = os.environ.get(llm_cfg["env_key"])
    if not api_key:
        raise RuntimeError(
            f"Environment variable {llm_cfg['env_key']} is not set"
        )

    model = llm_cfg["model"]
    system_prompt = config["translation"]["system_prompt"]
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model}:generateContent?key={api_key}"
    )

    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {
                "parts": [{"text": content}]
            }
        ],
    }

    resp = requests.post(url, json=payload, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Gemini API error {resp.status_code}: {resp.text}"
        )

    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected Gemini response: {data}") from exc


def call_deepseek(content, config):
    """Call DeepSeek API (OpenAI-compatible) to translate content.

    Args:
        content: English Markdown content to translate.
        config: Full config dict (from config.yaml).

    Returns:
        Translated content string.

    Raises:
        RuntimeError: If the API call fails.
    """
    llm_cfg = config["llm"]["fallback"]
    api_key = os.environ.get(llm_cfg["env_key"])
    if not api_key:
        raise RuntimeError(
            f"Environment variable {llm_cfg['env_key']} is not set"
        )

    model = llm_cfg["model"]
    system_prompt = config["translation"]["system_prompt"]
    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(
            f"DeepSeek API error {resp.status_code}: {resp.text}"
        )

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected DeepSeek response: {data}") from exc


def translate(content, config):
    """Translate content using primary backend, falling back to secondary.

    Args:
        content: English Markdown content to translate.
        config: Full config dict (from config.yaml).

    Returns:
        Translated content string.

    Raises:
        RuntimeError: If both backends fail.
    """
    primary_provider = config["llm"]["primary"]["provider"]
    fallback_provider = config["llm"]["fallback"]["provider"]

    backends = {
        "gemini": call_gemini,
        "deepseek": call_deepseek,
    }

    primary_fn = backends[primary_provider]
    fallback_fn = backends[fallback_provider]

    try:
        return primary_fn(content, config)
    except RuntimeError as primary_err:
        logger.warning("Primary backend (%s) failed: %s", primary_provider, primary_err)
        try:
            return fallback_fn(content, config)
        except RuntimeError as fallback_err:
            raise RuntimeError(
                f"All translation backends failed. "
                f"Primary ({primary_provider}): {primary_err}; "
                f"Fallback ({fallback_provider}): {fallback_err}"
            ) from fallback_err


def generate_slug(title):
    """Convert a title string to a URL-safe slug.

    Lowercases, replaces whitespace/special chars with hyphens,
    strips leading/trailing hyphens, and collapses consecutive hyphens.

    Args:
        title: The title string to slugify.

    Returns:
        A URL-safe slug string.
    """
    # Normalize unicode characters
    slug = unicodedata.normalize("NFKD", title)
    # Encode to ASCII, dropping non-ASCII chars
    slug = slug.encode("ascii", "ignore").decode("ascii")
    # Lowercase
    slug = slug.lower()
    # Replace any non-alphanumeric character with a hyphen
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Strip leading/trailing hyphens
    slug = slug.strip("-")
    return slug


def _resolve_relative_urls(content, source_url):
    """Convert relative image/link URLs in Markdown to absolute URLs.

    Uses the source URL to determine the base directory for resolution.
    For GitHub blob URLs, converts to raw.githubusercontent.com equivalents.
    """
    # Determine the base URL for resolving relative paths
    base_url = source_url
    # Convert GitHub blob URLs to raw URLs for asset resolution
    gh_match = re.match(
        r"https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.*)", source_url
    )
    if gh_match:
        owner, repo, ref, file_path = gh_match.groups()
        # Base is the directory containing the file
        dir_path = file_path.rsplit("/", 1)[0] + "/" if "/" in file_path else ""
        base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{dir_path}"

    def _replace_url(match):
        prefix = match.group(1)  # ![ or [
        alt = match.group(2)
        url = match.group(3)
        # Only resolve relative URLs (skip absolute, protocol-relative, anchors)
        if url.startswith(("http://", "https://", "//", "#")):
            return match.group(0)
        resolved = urljoin(base_url, url)
        return f"{prefix}{alt}]({resolved})"

    # Match markdown images ![alt](url) and links [text](url)
    return re.sub(r"(!?\[)([^\]]*)\]\(([^)]+)\)", _replace_url, content)


def write_translated_file(title, translated_content, source_url, date_str, config, slug_title=None):
    """Write a translated Markdown file with YAML frontmatter.

    Args:
        title: Translated title (Chinese).
        translated_content: Translated body content (Chinese Markdown).
        source_url: URL of the original English source.
        date_str: Date string in YYYY-MM-DD format.
        config: Full config dict (from config.yaml).
        slug_title: Optional English title to use for slug generation.
            Falls back to title if not provided.

    Returns:
        Absolute path to the written file.
    """
    tips_dir = config["output"]["tips_dir"]
    # Resolve relative to project root (parent of scripts/)
    if not os.path.isabs(tips_dir):
        project_root = os.path.dirname(os.path.dirname(__file__))
        tips_dir = os.path.join(project_root, tips_dir)

    os.makedirs(tips_dir, exist_ok=True)

    slug = generate_slug(slug_title or title)
    filename = f"{date_str}-{slug}.md"
    filepath = os.path.join(tips_dir, filename)

    # Determine source name from URL or default
    source_name = "claude-code"
    if "anthropic.com" in source_url:
        source_name = "anthropic-docs"
    elif "github.com" in source_url:
        source_name = "github"

    frontmatter = (
        f'---\n'
        f'title: "{title}"\n'
        f'date: {date_str}\n'
        f'source: "{source_name}"\n'
        f'original_url: "{source_url}"\n'
        f'---\n'
    )

    # Resolve relative URLs in content to absolute URLs
    translated_content = _resolve_relative_urls(translated_content, source_url)

    body = (
        f"\n# {title}\n"
        f"\n[查看原文]({source_url})\n"
        f"\n{translated_content}\n"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter + body)

    return filepath


def translate_items(items, config):
    """Translate a list of scraper output items and write files.

    Each item is expected to be a dict with keys:
        - title: English title
        - content: English Markdown content
        - url: Source URL
        - date (optional): Date string YYYY-MM-DD; defaults to today

    Args:
        items: List of item dicts from the scraper.
        config: Full config dict (from config.yaml).

    Returns:
        List of absolute file paths that were written.
    """
    output_paths = []

    for item in items:
        title = item["title"]
        content = item["content"]
        source_url = item["url"]
        date_str = item.get("date", datetime.now().strftime("%Y-%m-%d"))

        try:
            # Translate both the title and the body together, separated by a marker
            combined = f"# {title}\n\n{content}"
            translated = translate(combined, config)
        except RuntimeError:
            logger.warning(
                "Failed to translate '%s', using original content", title
            )
            translated = combined

        # Extract the translated title from the first heading line
        translated_lines = translated.strip().splitlines()
        translated_title = title  # fallback
        body_start = 0

        for i, line in enumerate(translated_lines):
            stripped = line.strip()
            if stripped.startswith("# "):
                translated_title = stripped[2:].strip()
                body_start = i + 1
                break

        translated_body = "\n".join(translated_lines[body_start:]).strip()

        # Use the original English title for slug generation since
        # generate_slug strips non-ASCII characters
        filepath = write_translated_file(
            translated_title,
            translated_body,
            source_url,
            date_str,
            config,
            slug_title=title,
        )
        output_paths.append(filepath)
        logger.info("Translated: %s -> %s", title, filepath)

    return output_paths


if __name__ == "__main__":
    cfg = load_config()

    # Example usage with a sample item
    sample_items = [
        {
            "title": "Using Context Window Efficiently",
            "content": (
                "When working with Claude Code, manage your context window carefully.\n\n"
                "```bash\ndu -sh ~/.claude\n```\n\n"
                "Use `/compact` to reduce token usage when the conversation gets long."
            ),
            "url": "https://docs.anthropic.com/en/docs/claude-code/overview",
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
    ]

    paths = translate_items(sample_items, cfg)
    for p in paths:
        print(f"Output: {p}")
