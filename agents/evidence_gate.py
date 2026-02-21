"""
Evidence Gate - Hard blocker for weakly supported claims
"""
import json
import re
from pathlib import Path
from agents.utils import (
    get_anthropic_client,
    load_markdown,
    save_json,
    print_section,
    print_success,
    print_error,
    print_warning,
    print_info
)


def run_evidence_gate(draft_path):
    """
    Run evidence gate on draft
    Returns: (passed: bool, claim_table: dict, issues: list)
    """
    print_section("EVIDENCE GATE")

    # Load draft
    try:
        draft = load_markdown(draft_path)
        print_success(f"Draft loaded: {draft_path}")
    except Exception as e:
        print_error(f"Could not load draft: {e}")
        return False, {}, [f"Could not load draft: {e}"]

    draft_text = draft['body']
    word_count = len(draft_text.split())
    print_info(f"Draft length: {word_count} words")

    # Extract claims from draft
    print_info("Extracting claims from draft...")
    claims = extract_claims(draft_text)
    print_info(f"Found {len(claims)} claims to verify")

    # Verify each claim
    print_info("Verifying claims against evidence...")
    client = get_anthropic_client()

    verification_results = []
    issues = []

    for i, claim in enumerate(claims, 1):
        claim_text = claim.get('claim_text', claim.get('text', 'Unknown claim'))
        print(f"  [{i}/{len(claims)}] Verifying: {claim_text[:80]}...")

        result = verify_single_claim(client, claim, draft_text)
        verification_results.append(result)

        if result['status'] == 'fail':
            issues.append(result)
            print_error(f"    FAIL: {result['reason']}")
        elif result['status'] == 'warning':
            print_warning(f"    WARNING: {result['reason']}")
        else:
            print_success(f"    PASS")

    # Check for risky content
    print_info("Checking for risky content...")
    risky_content = check_risky_content(draft_text)
    if risky_content:
        issues.extend(risky_content)
        for risk in risky_content:
            print_error(f"  RISKY: {risk['reason']}")

    # Generate claim table
    claim_table = {
        'draft_path': draft_path,
        'generated_at': Path(draft_path).stat().st_mtime,
        'word_count': word_count,
        'total_claims': len(claims),
        'claims': verification_results,
        'gate_status': 'PASSED' if not issues else 'FAILED',
        'issues': issues
    }

    # Print summary
    print()
    print("="*70)
    if issues:
        print_error(f"GATE FAILED: {len(issues)} blocking issues found")
        print()
        print("Issues:")
        for issue in issues:
            print(f"  • {issue.get('reason', 'Unknown issue')}")
            if 'claim_text' in issue:
                print(f"    Claim: \"{issue['claim_text'][:100]}...\"")
    else:
        print_success("GATE PASSED: All claims verified")

    print("="*70)
    print()

    return len(issues) == 0, claim_table, issues


def extract_claims(text):
    """
    Extract factual claims from draft text
    Returns list of {text, paragraph_index}
    """
    client = get_anthropic_client()

    prompt = f"""Extract all factual claims from this draft that require evidence/citation:

DRAFT:
{text}

For each claim, identify:
1. The specific factual assertion
2. Whether it needs a source/citation
3. The confidence level implied

Return a JSON array of claims:
[
  {{"claim_id": 1, "claim_text": "...", "needs_evidence": true, "implied_confidence": "high"}},
  ...
]

Focus on quantitative claims, market structure assertions, and mechanism explanations.
Exclude: definitions, obvious truths, logical deductions."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text

    # Extract JSON
    try:
        start = result_text.find('[')
        end = result_text.rfind(']') + 1
        if start != -1 and end > start:
            claims_data = json.loads(result_text[start:end])
            return [c for c in claims_data if c.get('needs_evidence', True)]
    except:
        pass

    return []


def verify_single_claim(client, claim, full_draft):
    """
    Verify a single claim
    Returns: {status: 'pass'|'warning'|'fail', reason, evidence_urls, confidence}
    """
    claim_text = claim['claim_text']

    # Check if claim has citation in draft
    urls = extract_urls_near_claim(full_draft, claim_text)

    prompt = f"""Verify this claim:

CLAIM: "{claim_text}"

DRAFT CONTEXT (for finding citations):
{full_draft[:3000]}

CITED URLS NEARBY:
{chr(10).join(urls) if urls else "No URLs found"}

Assess:
1. Does the claim have a credible source cited?
2. Is the claim appropriately hedged for its evidence?
3. Is it overstated relative to available evidence?

Return JSON:
{{
  "status": "pass"|"warning"|"fail",
  "reason": "explanation",
  "evidence_urls": ["url1", "url2"],
  "confidence_assessment": "appropriate"|"overstated"|"understated",
  "suggested_revision": "if needed"
}}

FAIL if: no credible source, claim is overstated, or appears to be speculation presented as fact.
WARNING if: weak source, hedge needed, or missing context.
PASS if: claim has credible source and appropriate confidence level."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text

    # Extract JSON
    try:
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start != -1 and end > start:
            result = json.loads(result_text[start:end])
            result['claim_text'] = claim_text
            return result
    except:
        pass

    # Fallback
    return {
        'claim_text': claim_text,
        'status': 'warning',
        'reason': 'Could not verify claim automatically',
        'evidence_urls': urls,
        'confidence_assessment': 'unknown'
    }


def extract_urls_near_claim(text, claim_text):
    """Extract URLs within 500 chars of claim"""
    # Find claim position
    claim_pos = text.lower().find(claim_text.lower())
    if claim_pos == -1:
        claim_pos = 0

    # Get context around claim
    start = max(0, claim_pos - 500)
    end = min(len(text), claim_pos + len(claim_text) + 500)
    context = text[start:end]

    # Extract URLs
    url_pattern = r'https?://[^\s\)"\']+'
    urls = re.findall(url_pattern, context)

    return urls


def check_risky_content(text):
    """Check for risky content patterns"""
    issues = []

    # Check for venue-specific exploitation guidance
    risky_patterns = [
        (r'exploit\s+\w+\s+exchange', 'Appears to describe venue-specific exploitation'),
        (r'take advantage of.+vulnerability', 'May describe vulnerability exploitation'),
        (r'backdoor|loophole|trick', 'Contains potentially manipulative language'),
    ]

    for pattern, reason in risky_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append({
                'status': 'fail',
                'reason': reason,
                'claim_text': 'Risky content detected',
                'type': 'risky_content'
            })

    # Check for undefined technical terms
    # TODO: Cross-reference with glossary

    return issues
