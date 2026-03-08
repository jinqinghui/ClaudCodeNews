"""Main pipeline script.

Chains scraper -> translator -> file writer to sync Claude Code tips.
"""

import logging
import sys

from scraper import save_manifest, scrape_all
from translator import translate_items

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Run the full sync pipeline: scrape -> translate -> write."""
    logger.info("Starting Claude Code tips sync pipeline")

    # Step 1: Scrape for new content
    items, manifest, config = scrape_all()

    if not items:
        logger.info("No new content found. Nothing to translate.")
        return 0

    logger.info("Found %d new item(s) to translate", len(items))

    # Step 2: Adapt scraper output keys to translator input format
    translator_items = []
    for item in items:
        translator_items.append({
            "title": item["title"],
            "content": item["content_md"],
            "url": item["source_url"],
            "date": item["fetched_at"][:10],  # YYYY-MM-DD from ISO timestamp
        })

    # Step 3: Translate and write files
    output_paths = translate_items(translator_items, config)

    # Step 4: Save manifest only after successful translation
    save_manifest(manifest, config)

    logger.info("Pipeline complete. Wrote %d translated file(s):", len(output_paths))
    for path in output_paths:
        logger.info("  %s", path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
