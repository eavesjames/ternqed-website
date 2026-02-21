"""
Intake Agent (Daily Automation)
Fetches and processes sources into structured briefs
"""
import json
from datetime import datetime
from pathlib import Path
from agents.utils import (
    save_json,
    get_date_slug,
    print_section,
    print_success,
    print_info,
    print_warning
)


def run_intake(sources_config=None):
    """
    Run daily intake process

    TODO: Implement actual RSS/source fetching
    For now, creates a placeholder structure
    """
    print_section("DAILY INTAKE")

    if not sources_config:
        sources_config = 'config/sources.json'

    print_info(f"Loading sources config: {sources_config}")
    print_warning("Intake agent not yet fully implemented")
    print_info("Creating placeholder intake brief...")

    # Placeholder intake brief
    date_slug = get_date_slug()
    intake_brief = {
        'date': datetime.now().isoformat(),
        'sources_processed': 0,
        'briefs': [],
        'status': 'placeholder'
    }

    output_path = f"data/intake/{date_slug}.json"
    save_json(intake_brief, output_path)

    print_success(f"Intake brief saved: {output_path}")
    print()
    print_info("To implement:")
    print("  1. Add RSS feed parser")
    print("  2. Add web scraping for key sources")
    print("  3. Add LLM-based brief generation")
    print("  4. Add deduplication against previous intake")
