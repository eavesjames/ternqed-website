"""
Finalization Agent (Friday Automation)
Finalizes draft, runs evidence gate, generates artifacts, creates PR
"""
import yaml
from pathlib import Path
from datetime import datetime
from agents.utils import (
    get_anthropic_client,
    load_markdown,
    save_markdown,
    save_json,
    get_date_slug,
    print_section,
    print_success,
    print_error,
    print_warning,
    print_info
)
from agents.evidence_gate import run_evidence_gate


def finalize_post(draft_path, skip_gate=False, no_pr=False):
    """
    Finalize draft and prepare for publishing

    Steps:
    1. Run evidence gate
    2. Generate/update frontmatter
    3. Add internal links
    4. Generate claim table
    5. Generate social drafts
    6. Create PR (if not --no-pr)
    """
    print_section("FINALIZE DRAFT")

    draft_path = Path(draft_path)
    if not draft_path.exists():
        print_error(f"Draft not found: {draft_path}")
        return

    # Load draft
    draft = load_markdown(str(draft_path))
    print_success(f"Draft loaded: {draft_path.name}")
    print_info(f"Word count: {len(draft['body'].split())} words")

    # Step 1: Evidence gate
    if not skip_gate:
        print()
        passed, claim_table, issues = run_evidence_gate(str(draft_path))

        if not passed:
            print()
            print_error("Cannot finalize: Evidence gate failed")
            print_info("Fix the issues above and re-run finalize")
            return

        # Save claim table
        claim_table_path = f"data/claims/{draft_path.stem}.json"
        save_json(claim_table, claim_table_path)
        print_success(f"Claim table saved: {claim_table_path}")
    else:
        print_warning("Skipping evidence gate (--skip-gate)")
        claim_table = {}

    # Step 2: Generate/update frontmatter
    print()
    print_info("Generating frontmatter metadata...")
    frontmatter = generate_frontmatter(draft['body'], draft.get('frontmatter', ''))
    print_success("Frontmatter generated")

    # Step 3: Add internal links
    print()
    print_info("Suggesting internal links...")
    updated_body = suggest_internal_links(draft['body'])
    if updated_body != draft['body']:
        print_success("Added internal link suggestions (marked with <!-- SUGGESTED -->)")
    else:
        print_info("No new internal links suggested")

    # Save updated draft
    save_markdown(str(draft_path), frontmatter, updated_body)
    print_success(f"Draft updated: {draft_path}")

    # Step 4: Generate social drafts
    print()
    print_info("Generating social media drafts...")
    social_drafts = generate_social_drafts(draft['body'], frontmatter)
    social_path = f"data/social/{draft_path.stem}.json"
    save_json(social_drafts, social_path)
    print_success(f"Social drafts saved: {social_path}")

    # Step 5: Summary
    print()
    print_section("FINALIZATION COMPLETE")
    print_success("Draft ready for publishing!")
    print()
    print("Artifacts created:")
    print(f"  • Draft: {draft_path}")
    if not skip_gate:
        print(f"  • Claim table: {claim_table_path}")
    print(f"  • Social drafts: {social_path}")
    print()
    print("Next steps:")
    print("  1. Review the updated draft")
    print("  2. Commit and push to GitHub")
    print("  3. Create pull request")
    if not no_pr:
        print_info("\nTo auto-create PR, re-run without --no-pr")


def generate_frontmatter(body, existing_frontmatter=''):
    """Generate frontmatter from body content"""
    client = get_anthropic_client()

    # Parse existing frontmatter if any
    existing_data = {}
    if existing_frontmatter:
        try:
            existing_data = yaml.safe_load(existing_frontmatter)
        except:
            pass

    prompt = f"""Analyze this draft and generate Hugo frontmatter:

DRAFT:
{body[:3000]}

EXISTING FRONTMATTER (if any):
{existing_frontmatter}

Generate complete frontmatter with:
- title (if not exists)
- date (today if not exists)
- description (150-170 chars, SEO-optimized)
- markets: ["equities"|"crypto"|"both"]
- mechanisms: [1-6] (adverse selection=1, inventory risk=2, coordination cost=3, arbitrage=4, info asymmetry=5, queue priority=6)
- latency_budget: ["propagation","processing","queuing","jitter"]
- mean_vs_tail: ["mean"|"tail"|"both"]
- status: ["reference"|"working-notes"|"speculation"]
- confidence: ["high"|"medium"|"low"]
- sources: [URLs cited in draft]

Return as valid YAML (not JSON). Preserve existing fields unless they need updating."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text

    # Extract YAML
    try:
        # Find YAML block
        if '```' in result_text:
            start = result_text.find('```') + 3
            if result_text[start:start+4] == 'yaml':
                start += 4
            end = result_text.find('```', start)
            yaml_text = result_text[start:end].strip()
        else:
            yaml_text = result_text.strip()

        frontmatter_data = yaml.safe_load(yaml_text)

        # Ensure required fields
        if 'date' not in frontmatter_data:
            frontmatter_data['date'] = datetime.now().strftime('%Y-%m-%d')

        return frontmatter_data

    except Exception as e:
        print_warning(f"Could not parse frontmatter: {e}")
        # Return existing or minimal
        return existing_data or {
            'title': 'Untitled',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'draft': True
        }


def suggest_internal_links(body):
    """Suggest internal links to evergreen hubs"""
    client = get_anthropic_client()

    # List of evergreen hubs (TODO: load dynamically)
    evergreen_hubs = [
        {"slug": "adverse-selection", "title": "Adverse Selection"},
        {"slug": "inventory-risk", "title": "Inventory Risk"},
        {"slug": "coordination-cost", "title": "Coordination Cost"},
        {"slug": "arbitrage-capture", "title": "Arbitrage Capture"},
        {"slug": "information-asymmetry", "title": "Information Asymmetry"},
        {"slug": "queue-priority", "title": "Queue Priority"}
    ]

    prompt = f"""Analyze this draft and suggest 2-5 internal links to evergreen hubs:

DRAFT:
{body[:2500]}

AVAILABLE EVERGREEN HUBS:
{chr(10).join([f"- /evergreen/{h['slug']}/ ({h['title']})" for h in evergreen_hubs])}

For each suggested link:
1. Identify the sentence or phrase to link
2. Specify which evergreen hub to link to
3. Explain why

Return as JSON:
[
  {{"phrase": "...", "hub_slug": "...", "reason": "..."}},
  ...
]

Only suggest links that add value - don't over-link."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        temperature=0.5,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text

    # For now, just add as comments (human decides whether to add)
    updated_body = body

    try:
        import json
        start = result_text.find('[')
        end = result_text.rfind(']') + 1
        if start != -1 and end > start:
            suggestions = json.loads(result_text[start:end])

            if suggestions:
                updated_body += "\n\n<!-- SUGGESTED INTERNAL LINKS:\n"
                for s in suggestions:
                    updated_body += f"- Link '{s['phrase']}' to /evergreen/{s['hub_slug']}/\n"
                    updated_body += f"  Reason: {s['reason']}\n"
                updated_body += "-->\n"

    except:
        pass

    return updated_body


def generate_social_drafts(body, frontmatter):
    """Generate social media drafts"""
    client = get_anthropic_client()

    title = frontmatter.get('title', 'Untitled')
    description = frontmatter.get('description', '')

    prompt = f"""Generate social media drafts for this article:

TITLE: {title}

DESCRIPTION: {description}

BODY EXCERPT:
{body[:2000]}

Generate:
1. LinkedIn Post (Variant A) - Professional, insight-focused (200-250 words)
2. LinkedIn Post (Variant B) - Question/hook-driven (150-200 words)
3. X Thread (5-7 tweets) - Technical, data-driven
4. 3 Community Discussion Prompts - Open-ended questions to spark discussion

Return as JSON:
{{
  "linkedin_a": "...",
  "linkedin_b": "...",
  "x_thread": ["tweet1", "tweet2", ...],
  "community_prompts": ["...", "...", "..."]
}}

Guidelines:
- LinkedIn: Professional tone, cite data, thought-provoking
- X: Punchy, technical, thread format
- Prompts: Open questions that invite expertise"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2500,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text

    # Extract JSON
    try:
        import json
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(result_text[start:end])
    except:
        pass

    return {
        "linkedin_a": "Draft generation failed",
        "linkedin_b": "Draft generation failed",
        "x_thread": [],
        "community_prompts": []
    }
