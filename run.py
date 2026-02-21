#!/usr/bin/env python3
"""
TernQED Research Engine - Human-AI Collaboration CLI
Orchestrates research prep, writing assistance, and finalization
"""
import sys
import argparse
from pathlib import Path

# Agent imports (will create these next)
from agents.research_prep import research_prep
from agents.assistant import interactive_assistant
from agents.finalize import finalize_post
from agents.intake import run_intake
from agents.evidence_gate import run_evidence_gate


def main():
    parser = argparse.ArgumentParser(
        description='TernQED Research Engine CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monday: Prepare research for writing
  python3 run.py research --topic "tail latency in arbitrage"

  # Tuesday-Thursday: Interactive writing assistant
  python3 run.py assist --research data/research/2026-02-24-tail-latency.json

  # Friday: Finalize draft and create PR
  python3 run.py finalize --draft content/posts/tail-latency-arbitrage.md

  # Daily automation (runs automatically)
  python3 run.py intake
  python3 run.py brief
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Research prep command (Monday automation)
    research_parser = subparsers.add_parser(
        'research',
        help='Prepare research summary for writing (Monday automation)'
    )
    research_parser.add_argument('--topic', required=True, help='Research topic/angle')
    research_parser.add_argument('--days', type=int, default=7, help='Days of intake to analyze')
    research_parser.add_argument('--min-sources', type=int, default=10, help='Minimum relevant sources')

    # Interactive assistant command (Tuesday-Thursday)
    assist_parser = subparsers.add_parser(
        'assist',
        help='Interactive writing assistant (Tuesday-Thursday)'
    )
    assist_parser.add_argument('--research', required=True, help='Path to research JSON')
    assist_parser.add_argument('--draft', help='Optional: path to draft in progress')

    # Finalize command (Friday automation)
    finalize_parser = subparsers.add_parser(
        'finalize',
        help='Finalize draft and create PR (Friday automation)'
    )
    finalize_parser.add_argument('--draft', required=True, help='Path to draft Markdown file')
    finalize_parser.add_argument('--skip-gate', action='store_true', help='Skip evidence gate')
    finalize_parser.add_argument('--no-pr', action='store_true', help='Skip PR creation')

    # Intake command (daily automation)
    intake_parser = subparsers.add_parser(
        'intake',
        help='Run daily intake (fetch + parse sources)'
    )
    intake_parser.add_argument('--sources', help='Path to sources config')

    # Brief command (daily automation)
    brief_parser = subparsers.add_parser(
        'brief',
        help='Create structured briefs from intake'
    )
    brief_parser.add_argument('--date', help='Date to process (YYYY-MM-DD)')

    # Evidence gate command (standalone)
    gate_parser = subparsers.add_parser(
        'gate',
        help='Run evidence gate on draft'
    )
    gate_parser.add_argument('--draft', required=True, help='Path to draft')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to appropriate agent
    try:
        if args.command == 'research':
            research_prep(args.topic, args.days, args.min_sources)

        elif args.command == 'assist':
            interactive_assistant(args.research, args.draft)

        elif args.command == 'finalize':
            finalize_post(args.draft, args.skip_gate, args.no_pr)

        elif args.command == 'intake':
            run_intake(args.sources)

        elif args.command == 'brief':
            brief_parser.print_help()
            print("\n⚠ Brief command not yet implemented")

        elif args.command == 'gate':
            run_evidence_gate(args.draft)

    except KeyboardInterrupt:
        print("\n\n⊘ Interrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
