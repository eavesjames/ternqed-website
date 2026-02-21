"""
Research Prep Agent (Monday Automation)
Analyzes intake briefs and prepares research summary for human writer
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from agents.utils import (
    get_anthropic_client,
    save_json,
    get_date_slug,
    print_section,
    print_success,
    print_error,
    print_info,
    print_warning
)


def load_recent_intake(days=7):
    """Load intake briefs from past N days"""
    intake_dir = Path('data/intake')
    if not intake_dir.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days)
    briefs = []

    for file in sorted(intake_dir.glob('*.json'), reverse=True):
        try:
            with open(file) as f:
                data = json.load(f)
                # Check if recent enough
                date_str = data.get('date', '')
                if date_str:
                    file_date = datetime.fromisoformat(date_str.split('T')[0])
                    if file_date >= cutoff:
                        # Handle both flat and nested formats
                        if 'briefs' in data:
                            # Nested format - extract briefs array
                            briefs.extend(data['briefs'])
                        else:
                            # Flat format - use data directly
                            briefs.append(data)
        except Exception as e:
            print_error(f"Could not load {file.name}: {e}")

    return briefs


def research_prep(topic, days=7, min_sources=10):
    """
    Prepare research summary for writing

    Args:
        topic: Research angle/topic to focus on
        days: How many days of intake to analyze
        min_sources: Minimum number of relevant sources needed
    """
    print_section(f"RESEARCH PREP: {topic}")

    # Load recent intake
    print_info(f"Loading intake briefs from past {days} days...")
    briefs = load_recent_intake(days)

    if not briefs:
        print_error("No intake briefs found. Run 'python3 run.py intake' first.")
        return

    print_success(f"Loaded {len(briefs)} intake briefs")

    # Prepare context for Claude
    intake_text = "\n\n".join([
        f"Source: {b.get('title', 'Unknown')}\nURL: {b.get('url', '')}\nSummary: {b.get('summary', '')}"
        for b in briefs[:50]  # Limit to avoid token overflow
    ])

    print_info(f"Analyzing sources for topic: '{topic}'...")

    # Call Claude to analyze and extract relevant information
    client = get_anthropic_client()

    prompt = f"""You are a research assistant preparing materials for a writer working on an article about latency value in electronic markets.

TOPIC: {topic}

INTAKE SOURCES (past {days} days):
{intake_text}

Your task:
1. Identify sources relevant to the topic (aim for at least {min_sources})
2. Extract key claims, data points, and quotes from each relevant source
3. Group findings by mechanism (adverse selection, inventory risk, coordination cost, arbitrage, information asymmetry, queue priority)
4. Note any contrasts between equities and crypto markets
5. Identify gaps or open questions

Output a structured JSON research summary with:
- relevant_sources: array of {{url, title, relevance_score, key_claims}}
- extracted_claims: array of {{claim_text, source_url, evidence_snippet, confidence}}
- mechanisms: object mapping mechanism names to relevant claims
- market_contrasts: {{equities: [...], crypto: [...], both: [...]}}
- open_questions: array of unanswered questions or gaps
- synthesis_suggestions: 2-3 paragraph narrative angles

Be rigorous: only include claims with clear evidence from sources."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        temperature=0.3,  # Lower temperature for factual extraction
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    result_text = response.content[0].text

    # Extract JSON from response
    try:
        # Find JSON in response
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start != -1 and end > start:
            research_data = json.loads(result_text[start:end])
        else:
            # If no JSON, create structured output
            research_data = {
                "raw_response": result_text,
                "error": "Could not parse JSON from response"
            }
    except json.JSONDecodeError:
        research_data = {
            "raw_response": result_text,
            "error": "JSON decode error"
        }

    # Add metadata
    research_data['topic'] = topic
    research_data['generated_at'] = datetime.now().isoformat()
    research_data['intake_period_days'] = days
    research_data['total_sources_analyzed'] = len(briefs)

    # Save research summary
    date_slug = get_date_slug()
    topic_slug = topic.lower().replace(' ', '-').replace('/', '-')[:50]
    filename = f"data/research/{date_slug}-{topic_slug}.json"

    save_json(research_data, filename)

    print_success(f"Research summary saved: {filename}")

    # Print quick summary
    if 'relevant_sources' in research_data:
        num_sources = len(research_data.get('relevant_sources', []))
        num_claims = len(research_data.get('extracted_claims', []))
        print_info(f"Found {num_sources} relevant sources")
        print_info(f"Extracted {num_claims} claims with citations")

        if num_sources < min_sources:
            print_warning(f"Only found {num_sources} sources (target: {min_sources})")
            print_warning("Consider: broader search, more intake days, or different topic angle")

    # Generate HTML preview
    generate_preview(research_data, filename.replace('.json', '.html'))

    print()
    print_success("Research prep complete!")
    print(f"Next steps:")
    print(f"  1. Review research summary: {filename}")
    print(f"  2. Start writing in content/posts/")
    print(f"  3. Use: python3 run.py assist --research {filename}")


def generate_preview(research_data, html_path):
    """Generate HTML preview of research summary"""

    relevant_sources = research_data.get('relevant_sources', [])
    extracted_claims = research_data.get('extracted_claims', [])
    open_questions = research_data.get('open_questions', [])
    synthesis = research_data.get('synthesis_suggestions', '')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Summary: {research_data.get('topic', 'Unknown')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 30px; border-bottom: 2px solid #eee; padding-bottom: 5px; }}
        .source {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #4c6ef5; }}
        .claim {{ background: #f0f9ff; padding: 12px; margin: 8px 0; border-left: 3px solid #3b82f6; }}
        .question {{ background: #fef3c7; padding: 10px; margin: 6px 0; }}
        .meta {{ color: #666; font-size: 14px; }}
        code {{ background: #eee; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>Research Summary: {research_data.get('topic', 'Unknown')}</h1>
    <p class="meta">Generated: {research_data.get('generated_at', '')} | Sources analyzed: {research_data.get('total_sources_analyzed', 0)}</p>

    <h2>Synthesis Suggestions</h2>
    <p>{synthesis}</p>

    <h2>Relevant Sources ({len(relevant_sources)})</h2>
"""

    for source in relevant_sources:
        html += f"""
    <div class="source">
        <strong>{source.get('title', 'Unknown')}</strong><br>
        <a href="{source.get('url', '#')}">{source.get('url', '')}</a><br>
        <em>Relevance: {source.get('relevance_score', 'N/A')}</em><br>
        Key claims: {', '.join(source.get('key_claims', [])[:3])}
    </div>
"""

    html += f"""
    <h2>Extracted Claims ({len(extracted_claims)})</h2>
"""

    for claim in extracted_claims[:20]:  # Limit to first 20
        html += f"""
    <div class="claim">
        <strong>Claim:</strong> {claim.get('claim_text', '')}<br>
        <strong>Source:</strong> <a href="{claim.get('source_url', '#')}">{claim.get('source_url', '')}</a><br>
        <strong>Evidence:</strong> "{claim.get('evidence_snippet', '')}"<br>
        <strong>Confidence:</strong> {claim.get('confidence', 'unknown')}
    </div>
"""

    html += f"""
    <h2>Open Questions ({len(open_questions)})</h2>
"""

    for q in open_questions:
        html += f"""
    <div class="question">• {q}</div>
"""

    html += """
</body>
</html>
"""

    Path(html_path).parent.mkdir(parents=True, exist_ok=True)
    with open(html_path, 'w') as f:
        f.write(html)

    print_success(f"Preview generated: {html_path}")
    print_info("Open in browser to review research summary")
