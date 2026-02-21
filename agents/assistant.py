"""
Interactive Writing Assistant (Tuesday-Thursday)
Provides on-demand help while human is writing
"""
import json
from pathlib import Path
from agents.utils import (
    get_anthropic_client,
    load_json,
    load_markdown,
    print_section,
    print_success,
    print_info,
    print_warning
)


def interactive_assistant(research_path, draft_path=None):
    """
    Interactive CLI assistant for writing

    Commands:
        find source: <query>       - Find source from research corpus
        draft: <section description> - Draft a section
        verify: <claim>            - Verify claim against sources
        suggest links             - Suggest evergreen hub links
        help                       - Show commands
        exit                       - Exit assistant
    """
    print_section("WRITING ASSISTANT")

    # Load research context
    try:
        research_data = load_json(research_path)
        print_success(f"Research context loaded: {research_path}")

        num_sources = len(research_data.get('relevant_sources', []))
        num_claims = len(research_data.get('extracted_claims', []))
        print_info(f"Context: {num_sources} sources, {num_claims} claims")
    except Exception as e:
        print_warning(f"Could not load research: {e}")
        research_data = {}

    # Load draft if provided
    draft_content = None
    if draft_path:
        try:
            draft_content = load_markdown(draft_path)
            print_success(f"Draft loaded: {draft_path}")
            print_info(f"Draft length: {len(draft_content['body'])} characters")
        except Exception as e:
            print_warning(f"Could not load draft: {e}")

    print()
    print("Assistant ready. Type 'help' for commands.")
    print()

    client = get_anthropic_client()

    # Prepare research context for Claude
    research_context = format_research_for_claude(research_data)

    # Interactive loop
    while True:
        try:
            user_input = input("> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nExiting assistant.")
                break

            if user_input.lower() == 'help':
                show_help()
                continue

            # Parse command
            if user_input.lower().startswith('find source:'):
                query = user_input.split(':', 1)[1].strip()
                find_source(client, research_context, query)

            elif user_input.lower().startswith('draft:'):
                description = user_input.split(':', 1)[1].strip()
                draft_section(client, research_context, draft_content, description)

            elif user_input.lower().startswith('verify:'):
                claim = user_input.split(':', 1)[1].strip()
                verify_claim(client, research_context, claim)

            elif user_input.lower() == 'suggest links':
                suggest_links(client, draft_content, research_data)

            else:
                print_warning(f"Unknown command. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\n\nExiting assistant.")
            break
        except Exception as e:
            print_warning(f"Error: {e}")


def format_research_for_claude(research_data):
    """Format research data for Claude context"""
    sources = research_data.get('relevant_sources', [])
    claims = research_data.get('extracted_claims', [])

    context = "RESEARCH CONTEXT:\n\n"
    context += "SOURCES:\n"
    for i, source in enumerate(sources[:20], 1):  # Limit to avoid token overflow
        context += f"{i}. {source.get('title', 'Unknown')} - {source.get('url', '')}\n"
        context += f"   Relevance: {source.get('relevance_score', 'N/A')}\n"
        context += f"   Key claims: {', '.join(source.get('key_claims', [])[:3])}\n\n"

    context += "\nEXTRACTED CLAIMS:\n"
    for i, claim in enumerate(claims[:30], 1):
        context += f"{i}. \"{claim.get('claim_text', '')}\"\n"
        context += f"   Source: {claim.get('source_url', '')}\n"
        context += f"   Evidence: \"{claim.get('evidence_snippet', '')}\"\n"
        context += f"   Confidence: {claim.get('confidence', 'unknown')}\n\n"

    return context


def find_source(client, research_context, query):
    """Find source from research corpus"""
    print_info(f"Searching for: {query}")

    prompt = f"""{research_context}

The writer is looking for sources about: {query}

Search the research context and provide:
1. The 2-3 most relevant sources
2. Specific claims/data from those sources
3. Direct quotes if available

Format as:
1. [Title] - [URL]
   Claim: "..."
   Quote: "..."
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text
    print(f"\n{result}\n")


def draft_section(client, research_context, draft_content, description):
    """Draft a section based on description"""
    print_info(f"Drafting: {description}")

    draft_context = ""
    if draft_content:
        draft_context = f"\n\nCURRENT DRAFT (for context):\n{draft_content['body'][:2000]}"

    prompt = f"""{research_context}{draft_context}

The writer needs a draft of: {description}

Write a 2-3 paragraph draft that:
- Is grounded in the research context (cite sources)
- Focuses on mechanisms and latency budgets
- Uses precise technical language
- Includes specific claims with confidence levels

Draft:"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        temperature=0.7,  # Higher temperature for creative drafting
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text
    print(f"\n{result}\n")
    print_info("Copy to clipboard? (y/n)")


def verify_claim(client, research_context, claim):
    """Verify claim against sources"""
    print_info(f"Verifying: {claim}")

    prompt = f"""{research_context}

The writer wants to verify this claim: "{claim}"

Check the research context and assess:
1. Is this claim supported by the sources?
2. What is the confidence level? (high/medium/low)
3. Which specific sources support it?
4. Are there any caveats or limitations?
5. Should the claim be softened or strengthened?

Provide a verification report:"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text

    # Check for warnings
    if any(word in result.lower() for word in ['weak', 'unsupported', 'no evidence', 'soften']):
        print()
        print_warning("⚠ Claim may need revision:")
    else:
        print()
        print_success("✓ Claim appears supported:")

    print(f"\n{result}\n")


def suggest_links(client, draft_content, research_data):
    """Suggest evergreen hub links"""
    if not draft_content:
        print_warning("No draft loaded. Use --draft flag when starting assistant.")
        return

    print_info("Analyzing draft for internal linking opportunities...")

    # TODO: Load actual evergreen hub topics
    evergreen_hubs = [
        "/evergreen/adverse-selection/",
        "/evergreen/inventory-risk/",
        "/evergreen/coordination-cost/",
        "/evergreen/arbitrage-capture/",
        "/evergreen/information-asymmetry/",
        "/evergreen/queue-priority/"
    ]

    prompt = f"""DRAFT:
{draft_content['body'][:3000]}

AVAILABLE EVERGREEN HUBS:
{chr(10).join(evergreen_hubs)}

Suggest 2-5 evergreen hub links that would be relevant to add to this draft.
For each suggestion, explain why and where in the draft it should be linked."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        temperature=0.5,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text
    print(f"\n{result}\n")


def show_help():
    """Show available commands"""
    print("""
Available commands:

  find source: <query>       - Find source from research corpus
                               Example: find source: latency impact on spreads

  draft: <description>       - Draft a section
                               Example: draft: why tail latency matters more than mean

  verify: <claim>            - Verify claim against sources
                               Example: verify: 1ms improvement reduces spreads by 0.8bp

  suggest links              - Suggest evergreen hub links for current draft

  help                       - Show this help message

  exit                       - Exit assistant
    """)
