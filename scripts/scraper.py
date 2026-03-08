"""Content scraper module.

Fetches content from configured documentation sources (web pages and GitHub repos),
performs MD5-based deduplication against a processed manifest, and returns structured
JSON-compatible objects.
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.yaml"
GITHUB_API_BASE = "https://api.github.com"


def load_config():
    """Load configuration from scripts/config.yaml."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_manifest(config=None):
    """Load the processed-content manifest from disk.

    Returns a dict with keys ``processed`` (md5 -> metadata) and
    ``last_github_sha`` (source_name -> sha).
    """
    if config is None:
        config = load_config()

    manifest_path = SCRIPT_DIR.parent / config["output"]["manifest"]
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    data.setdefault("processed", {})
    data.setdefault("last_github_sha", {})
    return data


def save_manifest(manifest, config=None):
    """Persist the manifest back to disk."""
    if config is None:
        config = load_config()

    manifest_path = SCRIPT_DIR.parent / config["output"]["manifest"]
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _md5(text):
    """Return the hex MD5 digest of *text*."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _html_to_markdown(html):
    """Convert HTML to a simple Markdown representation using BeautifulSoup.

    This is intentionally minimal -- it extracts the visible text from the
    main content area and preserves basic structure.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Try to find the main content area
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find("div", {"role": "main"})
        or soup.find("div", class_="content")
        or soup.find("div", id="content")
        or soup.body
        or soup
    )

    # Remove script and style elements
    for tag in main.find_all(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    lines = []
    for element in main.descendants:
        if element.name and element.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(element.name[1])
            text = element.get_text(strip=True)
            if text:
                lines.append("")
                lines.append(f"{'#' * level} {text}")
                lines.append("")
        elif element.name == "p":
            text = element.get_text(strip=True)
            if text:
                lines.append(text)
                lines.append("")
        elif element.name == "li":
            text = element.get_text(strip=True)
            if text:
                lines.append(f"- {text}")
        elif element.name == "pre":
            code = element.get_text()
            lines.append("")
            lines.append(f"```\n{code}\n```")
            lines.append("")
        elif element.name == "code" and element.parent.name != "pre":
            # Inline code handled via get_text; skip here to avoid duplication.
            pass

    return "\n".join(lines).strip()


def fetch_web_source(source, manifest):
    """Fetch content from web URLs defined in a source config block.

    Parameters
    ----------
    source : dict
        A source entry with ``type: web`` and a ``urls`` list.
    manifest : dict
        The current manifest (used for deduplication).

    Returns
    -------
    list[dict]
        New (non-duplicate) content items.
    """
    results = []
    urls = source.get("urls", [])

    for url in urls:
        try:
            logger.info("Fetching web source: %s", url)
            resp = requests.get(url, timeout=30, headers={"User-Agent": "ClaudCodeNews-Scraper/1.0"})
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            continue

        content_md = _html_to_markdown(resp.text)
        content_hash = _md5(content_md)

        if content_hash in manifest["processed"]:
            logger.info("Skipping duplicate content from %s (hash %s)", url, content_hash)
            continue

        # Attempt to extract a title from the HTML
        soup = BeautifulSoup(resp.text, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else url

        item = {
            "source_url": url,
            "title": title,
            "content_md": content_md,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
        results.append(item)

        # Record in manifest
        manifest["processed"][content_hash] = {
            "source_url": url,
            "fetched_at": item["fetched_at"],
        }

    return results


def _match_github_paths(tree_paths, patterns):
    """Return tree paths that match any of the glob-style *patterns*.

    Supports simple wildcards:
    - ``**/*.md`` matches any ``.md`` file at any depth.
    - ``README.md`` matches an exact path component.
    - ``docs/*.md`` matches ``.md`` files directly under ``docs/``.
    """
    import fnmatch

    matched = []
    for tp in tree_paths:
        for pat in patterns:
            if fnmatch.fnmatch(tp, pat):
                matched.append(tp)
                break
    return matched


def fetch_github_source(source, manifest):
    """Fetch Markdown files from a public GitHub repository.

    Uses the GitHub API to:
    1. Check if there are new commits since the last recorded SHA.
    2. Fetch the repo tree to find files matching the configured paths.
    3. Download and deduplicate file contents.

    Parameters
    ----------
    source : dict
        A source entry with ``type: github``, plus ``owner``, ``repo``,
        and ``paths`` keys.
    manifest : dict
        The current manifest (used for dedup and SHA tracking).

    Returns
    -------
    list[dict]
        New (non-duplicate) content items.
    """
    owner = source["owner"]
    repo = source["repo"]
    source_name = source.get("name", f"{owner}/{repo}")
    paths = source.get("paths", [])
    results = []

    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "ClaudCodeNews-Scraper/1.0"}
    # Support optional auth token via environment variable
    gh_token = os.environ.get("GITHUB_TOKEN")
    if gh_token:
        headers["Authorization"] = f"token {gh_token}"

    # 1. Check latest commit SHA on the default branch
    try:
        commits_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits?per_page=1"
        resp = requests.get(commits_url, timeout=30, headers=headers)
        resp.raise_for_status()
        commits = resp.json()
        if not commits:
            logger.warning("No commits found for %s/%s", owner, repo)
            return results
        latest_sha = commits[0]["sha"]
    except requests.RequestException as exc:
        logger.error("Failed to fetch commits for %s/%s: %s", owner, repo, exc)
        return results

    last_sha = manifest["last_github_sha"].get(source_name)
    if latest_sha == last_sha:
        logger.info("No new commits for %s since %s", source_name, last_sha[:8])
        return results

    # 2. Get the repo tree to find matching files
    try:
        tree_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{latest_sha}?recursive=1"
        resp = requests.get(tree_url, timeout=30, headers=headers)
        resp.raise_for_status()
        tree_data = resp.json()
    except requests.RequestException as exc:
        logger.error("Failed to fetch tree for %s/%s: %s", owner, repo, exc)
        return results

    all_paths = [item["path"] for item in tree_data.get("tree", []) if item["type"] == "blob"]
    matched_paths = _match_github_paths(all_paths, paths)

    if not matched_paths:
        logger.info("No files matched patterns %s in %s/%s", paths, owner, repo)
        manifest["last_github_sha"][source_name] = latest_sha
        return results

    # 3. Fetch each matched file
    for file_path in matched_paths:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{latest_sha}/{file_path}"
        try:
            resp = requests.get(raw_url, timeout=30, headers={"User-Agent": "ClaudCodeNews-Scraper/1.0"})
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to fetch file %s: %s", file_path, exc)
            continue

        content_md = resp.text
        content_hash = _md5(content_md)

        if content_hash in manifest["processed"]:
            logger.info("Skipping duplicate file %s (hash %s)", file_path, content_hash)
            continue

        title = Path(file_path).stem.replace("-", " ").replace("_", " ").title()

        item = {
            "source_url": f"https://github.com/{owner}/{repo}/blob/{latest_sha}/{file_path}",
            "title": title,
            "content_md": content_md,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
        results.append(item)

        manifest["processed"][content_hash] = {
            "source_url": item["source_url"],
            "fetched_at": item["fetched_at"],
        }

    # Update last seen SHA
    manifest["last_github_sha"][source_name] = latest_sha
    return results


def scrape_all():
    """Run the full scrape pipeline.

    Loads config and manifest, iterates over all configured sources,
    and fetches new content. The manifest is updated in-memory but NOT
    saved to disk — the caller is responsible for calling
    ``save_manifest`` after successful downstream processing (e.g.
    translation) to avoid marking items as processed before they are
    fully handled.

    Returns
    -------
    tuple[list[dict], dict, dict]
        A 3-tuple of (items, manifest, config).
    """
    config = load_config()
    manifest = load_manifest(config)
    all_items = []

    for source in config.get("sources", []):
        source_type = source.get("type", "")
        source_name = source.get("name", source_type)

        try:
            if source_type == "web":
                items = fetch_web_source(source, manifest)
            elif source_type == "github":
                items = fetch_github_source(source, manifest)
            else:
                logger.warning("Unknown source type '%s' for source '%s'", source_type, source_name)
                continue

            logger.info("Fetched %d new item(s) from %s", len(items), source_name)
            all_items.extend(items)
        except Exception:
            logger.exception("Unexpected error processing source '%s'", source_name)
            continue

    logger.info("Scrape complete: %d new item(s) total", len(all_items))
    return all_items, manifest, config


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    items, manifest, config = scrape_all()
    print(json.dumps(items, indent=2, ensure_ascii=False))
    save_manifest(manifest, config)
